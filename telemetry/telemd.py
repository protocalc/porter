#!/usr/bin/env python3
"""
telemd.py  -  payload XBee radio daemon.

Starts at boot via systemd.  Owns the XBee device and listens for commands
from the ground station.  All device I/O runs in a single thread to avoid
concurrent-access issues with the digi-xbee library.

Supported commands (uplink, ground → payload):
  ping             reply "pong"
  getlog           send last 40kB of flight.log (base64-encoded)
  reboot           reboot the computer
  setconfig <path> overwrite config/default.yml with base64-encoded data
  shutdown         shut down the computer
  start            start control.py in the project venv
  stop             gracefully stop control.py
  camera.start     start a camera thread (Alvium only)
  camera.capture [-e <exposure>] [-g <gain>]  capture a single frame from the Alvium camera
  gimbal.goto <yaw> <pitch> <roll>  move gimbal to specified angles (degrees)
  gimbal.mode <mode>  set gimbal mode (off, lock, or follow)
  gimbal.starttrack  start pointing controller POI tracking (if configured)
  gimbal.stoptrack   stop pointing controller POI tracking
  $<shell command> run a shell command and return its output (base64-encoded
Every message ends with END_OF_MESSAGE_BYTE (0x00) as defined in Xbee.py.
"""

import base64
import json
import logging
import os
import shlex
import subprocess
import sys
import queue
import signal
import threading
import socket
import tempfile
import time
import uuid
import re

# global state for jobs that are running in the background (e.g. shell commands)
_jobs: dict[str, dict] = {}     # job_id -> {"proc", "outfile", "cmd", "start"}
_jobs_lock = threading.Lock()
JOB_POLL_INTERVAL = 0.5

# path setup
TELEMD_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, TELEMD_DIR)

# add porter_venv to sys.path so we can import parameters.py
PORTER_DIR = os.path.join(TELEMD_DIR, "..")
sys.path.insert(1, PORTER_DIR)
import parameters as params

from digi.xbee.exception import TimeoutException
from Xbee import Xbee, TransmitException, END_OF_MESSAGE_BYTE

# configuration 
XBEE_PORT     = "/dev/ttyUSB0"
XBEE_BAUDRATE = 38400
REMOTE_NAME   = "OBI"    # key in Xbee.IDs for the ground station
READ_TIMEOUT  = 0.2      # seconds per read_data call

FLIGHT_SCRIPT = os.path.join(TELEMD_DIR, "..", "control.py")
VENV_PYTHON   = os.path.join(params.home_directory, "porter_venv", "bin", "python3")
STATUS_FILE   = "/tmp/porter_status.json"
LOG_FILE      = os.path.join(params.home_directory, params.data_folder_name, params.current_symlink_name, params.logfile_name)
CONFIG_FILE   = os.path.join(TELEMD_DIR, "..", "config", "default.yml")
LOG_TAIL_BYTES    = 40960  # bytes sent in response to 'getlog'
SHELL_CMD_TIMEOUT = 10     # seconds before a shell command is killed
SHELL_QUICK_WAIT = 2.0     # seconds to wait before treating a command as a background job
CMDOUT_MAX_BYTES  = 2000   # output cap before base64 encoding
CAPTURE_SCRIPT  = os.path.join(TELEMD_DIR, "alvium_capture.py")
CAPTURE_OUTPUT  = os.path.join(TELEMD_DIR, "captured_frame.jpg")
CAPTURE_TIMEOUT = 60        # seconds to wait for a frame to be captured
CHRONY_TIMEOUT        = 2   # seconds to wait for a chronyc call
CHRONY_POLL_INTERVAL  = 5   # seconds between chrony status polls

CMD_SOCKET_PATH = "/tmp/porter_cmd.sock"
CMD_TIMEOUT = 5.0

# status of powerd daemon
POWER_CONTROLLER_ENABLED = True
POWER_CONTROLLER_STATUS_PATH = "/tmp/power_cmd.json"

# logging
_log_formatter = logging.Formatter("%(asctime)s [%(levelname)-8s] %(name)s: %(message)s")
_stream_handler = logging.StreamHandler(sys.stdout)
_stream_handler.setFormatter(_log_formatter)
logging.basicConfig(level=logging.INFO, handlers=[_stream_handler])
logger = logging.getLogger("telemd")

# shared state
_shutdown = threading.Event()
_outbound: "queue.Queue[str]" = queue.Queue()   # messages to send

_porter_process: "subprocess.Popen | None" = None
_porter_lock = threading.Lock()

_chrony_lock  = threading.Lock()
_chrony_cache: dict = {"ok": False, "error": "not polled yet"}


def _send_command(cmd: str, params: dict | None = None) -> dict:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(CMD_TIMEOUT)
        sock.connect(CMD_SOCKET_PATH)
        sock.sendall((json.dumps({"cmd": cmd, "params": params or {}}) + "\n").encode("utf-8"))
        data = b""
        while not data.endswith(b"\n"):
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        return json.loads(data.decode("utf-8"))

def _porter_start() -> str:
    global _porter_process
    with _porter_lock:
        if _porter_process is not None and _porter_process.poll() is None:
            return "ERR:porter already running"
        try:
            # Use a bash login shell so .profile is sourced and Vimba/SDK
            # environment variables (e.g. GENICAM_GENTL64_PATH) are available.
            _porter_process = subprocess.Popen(
                ["bash", "--login", "-c", f'"{VENV_PYTHON}" "{FLIGHT_SCRIPT}"'],
                cwd=TELEMD_DIR,
            )
            logger.info(f"porter started (PID {_porter_process.pid})")
            return f"ACK:porter_start PID={_porter_process.pid}"
        except Exception as e:
            logger.error(f"Failed to start porter: {e}")
            return f"ERR:porter_start failed: {e}"


def _porter_stop() -> str:
    global _porter_process
    with _porter_lock:
        if _porter_process is None or _porter_process.poll() is not None:
            return "ERR:porter is not running"
        proc = _porter_process
    try:
        proc.send_signal(signal.SIGINT)
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            logger.warning("porter did not stop in time, sending SIGTERM")
            proc.terminate()
            proc.wait(timeout=5)
        logger.info("porter stopped")
        return "ACK:porter_stop"
    except Exception as e:
        logger.error(f"Failed to stop porter: {e}")
        return f"ERR:porter_stop failed: {e}"

# chrony 
def _query_chrony() -> dict:
    """Ask chronyd what it's currently synced to and whether it's PPS."""
    try:
        result = subprocess.run(
            ["chronyc", "tracking"],
            capture_output=True, text=True, timeout=CHRONY_TIMEOUT,
        )
        if result.returncode != 0:
            return {"ok": False, "error": (result.stderr or "chronyc failed").strip()}

        info = {}
        for line in result.stdout.splitlines():
            if ":" not in line:
                continue
            key, _, val = line.partition(":")
            info[key.strip()] = val.strip()

        refid_line = info.get("Reference ID", "")
        m = re.search(r"\(([^)]+)\)", refid_line)
        ref_name = m.group(1) if m else refid_line or "unknown"

        offset_m = re.search(r"[-+]?\d*\.?\d+", info.get("Last offset", ""))
        offset_s = float(offset_m.group()) if offset_m else None

        try:
            stratum = int(info.get("Stratum", ""))
        except ValueError:
            stratum = None

        return {
            "ok": True,
            "ref": ref_name,
            "pps_selected": "pps" in ref_name.lower(),
            "stratum": stratum,
            "offset_s": offset_s,
            "leap_status": info.get("Leap status"),
        }
    except FileNotFoundError:
        return {"ok": False, "error": "chronyc not found"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "chronyc timed out"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _chrony_monitor() -> None:
    logger.info("Chrony monitor started")
    while not _shutdown.is_set():
        result = _query_chrony()
        with _chrony_lock:
            global _chrony_cache
            _chrony_cache = result
        if not result.get("ok"):
            logger.warning(f"chrony query failed: {result.get('error')}")
        _shutdown.wait(CHRONY_POLL_INTERVAL)
    logger.info("Chrony monitor stopped")

# command handler
def _handle(raw: bytes, antenna: Xbee) -> None:
    """Decode a complete received message and enqueue a reply."""
    cmd = raw.decode("utf-8", errors="replace").strip().lower()
    logger.info(f"RX: {cmd!r}")

    if cmd == "ping":
        value = antenna.device.get_parameter("DB")
        rssi_dbm = -int.from_bytes(value, byteorder='big')
        _outbound.put(f"pong - uplink RSSI: {rssi_dbm} dBm")

    elif cmd == "reboot":
        logger.warning("Reboot command received - rebooting in 3 s")
        _outbound.put("ACK:reboot")
        threading.Timer(3.0, lambda: subprocess.run(["sudo", "reboot"])).start()

    elif cmd == "shutdown":
        logger.warning("Shutdown command received - shutting down in 3 s")
        _outbound.put("ACK:shutdown")
        threading.Timer(3.0, lambda: subprocess.run(["sudo", "shutdown", "-h", "now"])).start()

    elif cmd == "start":
        _outbound.put(_porter_start())

    elif cmd == "stop":
        _outbound.put(_porter_stop())

    elif cmd == "getlog":
        try:
            with open(LOG_FILE, "rb") as f:
                f.seek(0, 2)  # seek to end
                size = f.tell()
                f.seek(max(0, size - LOG_TAIL_BYTES))
                tail = f.read()
            encoded = base64.b64encode(tail).decode("ascii")
            _outbound.put(f"LOGDATA:{encoded}")
            logger.info(f"Sending last {len(tail)} bytes of flight.log")
        except FileNotFoundError:
            _outbound.put("ERR:flight.log not found")
        except Exception as e:
            _outbound.put(f"ERR:getlog failed: {e}")

    elif cmd.startswith("camera.start"):
        try:
            resp = _send_command("camera.start")
            _outbound.put(f"ACK:camera.start {resp.get('detail','')}" if resp.get("ok")
                        else f"ERR:camera.start {resp.get('error','unknown error')}")
        except (ConnectionRefusedError, FileNotFoundError):
            _outbound.put("ERR:camera.start: command socket unavailable")
        except Exception as e:
            _outbound.put(f"ERR:camera.start: {e}")

    elif cmd.startswith("camera.capture"):
        raw_str = raw.decode("utf-8", errors="replace").strip()
        try:
            tokens = shlex.split(raw_str)
        except ValueError:
            tokens = raw_str.split()
        exposure, gain = 10000, 30.0
        i = 1
        while i < len(tokens):
            if tokens[i] == "-e" and i + 1 < len(tokens):
                try:
                    exposure = int(tokens[i + 1])
                except ValueError:
                    pass
                i += 2
            elif tokens[i] == "-g" and i + 1 < len(tokens):
                try:
                    gain = float(tokens[i + 1])
                except ValueError:
                    pass
                i += 2
            else:
                i += 1
        logger.info(f"Camera capture: exposure={exposure} gain={gain}")
        _outbound.put(f"ACK:camera.capture exposure={exposure} gain={gain} - capturing...")
        try:
            result = subprocess.run(
                ["bash", "--login", "-c",
                 f'"{VENV_PYTHON}" "{CAPTURE_SCRIPT}" --exposure {exposure} --gain {gain}'],
                cwd=os.path.dirname(CAPTURE_SCRIPT),
                capture_output=True,
                text=True,
                timeout=CAPTURE_TIMEOUT,
            )
            if result.returncode != 0:
                err = (result.stderr or result.stdout or "no output").strip()[:300]
                _outbound.put(f"ERR:camera.capture failed: {err}")
            else:
                with open(CAPTURE_OUTPUT, "rb") as f:
                    img_bytes = f.read()
                encoded = base64.b64encode(img_bytes).decode("ascii")
                _outbound.put(f"IMGDATA:{encoded}")
                logger.info(f"Sending captured frame ({len(img_bytes)} bytes JPEG)")
        except subprocess.TimeoutExpired:
            _outbound.put("ERR:camera.capture timed out")
        except FileNotFoundError:
            _outbound.put("ERR:camera.capture: captured_frame.jpg not found after capture")
        except Exception as e:
            _outbound.put(f"ERR:camera.capture: {e}")

    elif raw.startswith(b"gimbal.goto"):
        raw_str = raw.decode("utf-8", errors="replace").strip()
        try:
            tokens = shlex.split(raw_str)
        except ValueError:
            tokens = raw_str.split()
        yaw, pitch, roll = 0, 0, 0
        if len(tokens) >= 4:
            try:
                yaw = float(tokens[1])
                pitch = float(tokens[2])
                roll = float(tokens[3])
            except ValueError:
                _outbound.put("ERR:gimbal.goto: invalid angles")
                return
        try:
            resp = _send_command("gimbal.goto", {"yaw": yaw, "pitch": pitch, "roll": roll})
            _outbound.put(f"ACK:gimbal.goto {resp.get('detail','')}" if resp.get("ok")
                        else f"ERR:gimbal.goto {resp.get('error','unknown error')}")
        except (ConnectionRefusedError, FileNotFoundError):
            _outbound.put("ERR:gimbal.goto: command socket unavailable")
        except Exception as e:
            _outbound.put(f"ERR:gimbal.goto: {e}")

    elif raw.startswith(b"gimbal.mode"):
        raw_str = raw.decode("utf-8", errors="replace").strip()
        try:
            tokens = shlex.split(raw_str)
        except ValueError:
            tokens = raw_str.split()
        mode = "follow"
        if len(tokens) >= 2:
            mode = tokens[1]
        try:
            resp = _send_command("gimbal.mode", {"mode": mode})
            _outbound.put(f"ACK:gimbal.mode {resp.get('detail','')}" if resp.get("ok")
                        else f"ERR:gimbal.mode {resp.get('error','unknown error')}")
        except (ConnectionRefusedError, FileNotFoundError):
            _outbound.put("ERR:gimbal.mode: command socket unavailable")
        except Exception as e:
            _outbound.put(f"ERR:gimbal.mode: {e}")

    elif raw.startswith(b"gimbal.starttrack"):
        try:
            resp = _send_command("gimbal.starttrack")
            _outbound.put(f"ACK:gimbal.starttrack {resp.get('detail','')}" if resp.get("ok")
                        else f"ERR:gimbal.starttrack {resp.get('error','unknown error')}")
        except (ConnectionRefusedError, FileNotFoundError):
            _outbound.put("ERR:gimbal.starttrack: command socket unavailable")
        except Exception as e:
            _outbound.put(f"ERR:gimbal.starttrack: {e}")

    elif raw.startswith(b"gimbal.stoptrack"):
        try:
            resp = _send_command("gimbal.stoptrack")
            _outbound.put(f"ACK:gimbal.stoptrack {resp.get('detail','')}" if resp.get("ok")
                        else f"ERR:gimbal.stoptrack {resp.get('error','unknown error')}")
        except (ConnectionRefusedError, FileNotFoundError):
            _outbound.put("ERR:gimbal.stoptrack: command socket unavailable")
        except Exception as e:
            _outbound.put(f"ERR:gimbal.stoptrack: {e}")

    elif raw.startswith(b"$"):
        shell_cmd = raw[1:].decode("utf-8", errors="replace").strip()
        job_id = uuid.uuid4().hex[:8]
        logger.info(f"Shell cmd {job_id}: {shell_cmd!r}")
        try:
            outfile = tempfile.NamedTemporaryFile(
                delete=False, prefix=f"job_{job_id}_", suffix=".log", dir="/tmp"
            )
            proc = subprocess.Popen(
                shell_cmd,
                shell=True,
                stdout=outfile,
                stderr=subprocess.STDOUT,
                cwd=TELEMD_DIR,
                start_new_session=True,
            )
            outfile.close()

            try:
                retcode = proc.wait(timeout=SHELL_QUICK_WAIT)
                # finished quickly -> behave exactly like the old synchronous path
                with open(outfile.name, "rb") as f:
                    output = f.read()
                os.unlink(outfile.name)
                if not output:
                    output = f"(exit {retcode}, no output)".encode("utf-8")
                output = output[:CMDOUT_MAX_BYTES]
                encoded = base64.b64encode(output).decode("ascii")
                _outbound.put(f"CMDOUT:{encoded}")

            except subprocess.TimeoutExpired:
                # still running -> hand off to the background job tracker
                with _jobs_lock:
                    _jobs[job_id] = {
                        "proc": proc,
                        "outfile": outfile.name,
                        "cmd": shell_cmd,
                        "start": time.monotonic(),
                    }
                _outbound.put(f"ACK:job {job_id} started (PID {proc.pid}, still running): {shell_cmd}")

        except Exception as e:
            _outbound.put(f"ERR:shell failed: {e}")

    elif cmd == "jobs":
        with _jobs_lock:
            if not _jobs:
                _outbound.put("ACK:jobs none running")
            else:
                lines = []
                for jid, info in _jobs.items():
                    elapsed = time.monotonic() - info["start"]
                    lines.append(f"{jid} ({info['cmd'][:40]}) running {elapsed:.0f}s")
                _outbound.put("ACK:jobs" + " | ".join(lines))

    elif cmd.startswith("canceljob"):
        raw_str = raw.decode("utf-8", errors="replace").strip()
        tokens = raw_str.split()
        if len(tokens) < 2:
            _outbound.put("ERR:canceljob: missing job id")
        else:
            jid = tokens[1]
            with _jobs_lock:
                info = _jobs.get(jid)
            if info is None:
                _outbound.put(f"ERR:canceljob: no such job '{jid}'")
            else:
                try:
                    os.killpg(os.getpgid(info["proc"].pid), signal.SIGTERM)
                    _outbound.put(f"ACK:canceljob {jid} sent SIGTERM")
                except ProcessLookupError:
                    _outbound.put(f"ERR:canceljob {jid}: process already gone")
                except Exception as e:
                    _outbound.put(f"ERR:canceljob {jid}: {e}")

    elif raw.startswith(b"setconfig"):
        try:
            encoded = raw[len(b"setconfig"):]
            data = base64.b64decode(encoded)
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            tmp = CONFIG_FILE + ".tmp"
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, CONFIG_FILE)
            _outbound.put(f"ACK:setconfig ({len(data)} bytes written)")
            logger.info(f"config/default.yml overwritten ({len(data)} bytes)")
        except Exception as e:
            _outbound.put(f"ERR:setconfig failed: {e}")

    else:
        reply = f"ERR:unknown command '{cmd}'"
        logger.warning(reply)
        _outbound.put(reply)


# XBee I/O thread
def _io_thread(antenna: Xbee) -> None:
    """
    The ONLY thread that calls read_data / send_data on the device.
    Loop:
      1. Drain outbound queue → send each message.
      2. read_data(short timeout) → accumulate into rx_buf.
      3. When rx_buf ends with EOM byte → dispatch complete message.
    """
    logger.info("I/O thread started")
    rx_buf = b""

    while not _shutdown.is_set():

        # send everything queued
        while True:
            try:
                msg = _outbound.get_nowait()
            except queue.Empty:
                break
            try:
                if antenna.remote_device is not None:
                    antenna.send_msg(msg)
                else:
                    antenna.send_msg_broadcast(msg)
                logger.info(f"TX: {msg!r}")
            except TransmitException as e:
                logger.warning(f"Transmit failed: {e}")
            except Exception as e:
                logger.error(f"Send error: {e}")

        # try to receive one frame
        try:
            frame = antenna.device.read_data(timeout=READ_TIMEOUT)
        except TimeoutException:
            frame = None
        except Exception as e:
            if not _shutdown.is_set():
                logger.warning(f"read_data error: {e}")
            frame = None

        if frame is not None:
            rx_buf += frame.data
            if rx_buf.endswith(END_OF_MESSAGE_BYTE):
                _handle(rx_buf[:-1], antenna)
                rx_buf = b""
            elif len(rx_buf) > 80 * 1024:
                logger.warning("RX buffer overflow, discarding")
                rx_buf = b""

    logger.info("I/O thread stopped")


def _read_status() -> dict:
    try:
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _read_powerd_status() -> dict:
    try:
        with open(POWER_CONTROLLER_STATUS_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _telemetry_scheduler() -> None:
    """Send a TEL packet every second. No device access — only enqueues."""
    logger.info("Telemetry scheduler started")
    while not _shutdown.is_set():
        _shutdown.wait(1.0)
        status = _read_status()
        if POWER_CONTROLLER_ENABLED:
            powerd_status = _read_powerd_status()
            status["power_controller"] = powerd_status
        with _porter_lock:
            porter_running = (
                _porter_process is not None and _porter_process.poll() is None
            )
        status["porter"] = "running" if porter_running else "stopped"
        with _chrony_lock:
            status["chrony"] = dict(_chrony_cache)
        _outbound.put(f"TEL:{json.dumps(status, separators=(',', ':'))}")

def _job_monitor() -> None:
    """Poll running background jobs; report + clean up finished ones."""
    logger.info("Job monitor started")
    while not _shutdown.is_set():
        _shutdown.wait(JOB_POLL_INTERVAL)

        with _jobs_lock:
            job_ids = list(_jobs.keys())

        for jid in job_ids:
            with _jobs_lock:
                info = _jobs.get(jid)
            if info is None:
                continue

            proc = info["proc"]
            retcode = proc.poll()
            if retcode is None:
                continue   # still running

            try:
                with open(info["outfile"], "rb") as f:
                    output = f.read()
            except FileNotFoundError:
                output = b""
            finally:
                try:
                    os.unlink(info["outfile"])
                except FileNotFoundError:
                    pass

            elapsed = time.monotonic() - info["start"]
            output = output[:CMDOUT_MAX_BYTES]
            encoded = base64.b64encode(output).decode("ascii")
            status = "ok" if retcode == 0 else f"exit {retcode}"
            _outbound.put(f"ACK:job done {jid}:{status}:{elapsed:.1f}s:{encoded}")
            logger.info(f"Job {jid} finished ({status}, {elapsed:.1f}s)")

            with _jobs_lock:
                _jobs.pop(jid, None)

    logger.info("Job monitor stopped")

# main
def main() -> None:
    def _on_signal(signum, frame):
        logger.info(f"Caught {signal.strsignal(signum)}, shutting down")
        _shutdown.set()

    signal.signal(signal.SIGINT,  _on_signal)
    signal.signal(signal.SIGTERM, _on_signal)

    logger.info(f"telemd starting on {XBEE_PORT} @ {XBEE_BAUDRATE} baud, remote={REMOTE_NAME}")

    antenna = Xbee(port=XBEE_PORT, baudrate=XBEE_BAUDRATE)
    antenna.open(force_settings=True, remote_name=REMOTE_NAME)
    logger.info("XBee open")

    _outbound.put("telemd started")   # announce we are alive

    threads = [
        threading.Thread(target=_io_thread, args=(antenna,), daemon=True),
        threading.Thread(target=_telemetry_scheduler,        daemon=True),
        threading.Thread(target=_job_monitor,                daemon=True),
        threading.Thread(target=_chrony_monitor,             daemon=True),
    ]
    for t in threads:
        t.start()

    _shutdown.wait()

    logger.info("Closing XBee...")
    try:
        antenna.close()
    except Exception:
        pass
    logger.info("telemd stopped")


if __name__ == "__main__":
    main()