#!/usr/bin/env python3
"""
telemd.py  -  payload XBee radio daemon.

Starts at boot via systemd.  Owns the XBee device and listens for commands
from the ground station.  All device I/O runs in a single thread to avoid
concurrent-access issues with the digi-xbee library.

Supported commands (uplink, ground → payload):
  ping             reply "pong"
  getlog           send last 4kB of flight.log (base64-encoded)
  reboot           reboot the computer
  setconfig <path> overwrite config/default.yml with base64-encoded data
  shutdown         shut down the computer
  start            start control.py in the project venv
  stop             gracefully stop control.py
  camcap [-e <exposure>] [-g <gain>]  capture a single frame from the Alvium camera
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

# path setup
TELEMD_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, TELEMD_DIR)

from digi.xbee.exception import TimeoutException
from porter.telemetry.Xbee import Xbee, TransmitException, END_OF_MESSAGE_BYTE
import parameters as params

# configuration 
XBEE_PORT     = "/dev/ttyUSB0"
XBEE_BAUDRATE = 38400
REMOTE_NAME   = "OBI"    # key in Xbee.IDs for the ground station
READ_TIMEOUT  = 0.2      # seconds per read_data call

FLIGHT_SCRIPT = os.path.join(TELEMD_DIR, "control.py")
VENV_PYTHON   = "/home/polocalc/porter_venv/bin/python3"
STATUS_FILE   = "/tmp/porter_status.json"
LOG_FILE      = os.path.join(os.environ["HOME"], params.data_directory, params.current_symlink_name, params.logfile_name)
CONFIG_FILE   = os.path.join(TELEMD_DIR, "config", "default.yml")
LOG_TAIL_BYTES    = 40960  # bytes sent in response to 'getlog'
SHELL_CMD_TIMEOUT = 10     # seconds before a shell command is killed
CMDOUT_MAX_BYTES  = 2000   # output cap before base64 encoding
CAPTURE_SCRIPT  = os.path.join(TELEMD_DIR, "porter", "telemetry", "alvium_capture.py")
CAPTURE_OUTPUT  = os.path.join(TELEMD_DIR, "porter", "telemetry", "captured_frame.jpg")
CAPTURE_TIMEOUT = 30       # seconds to wait for a frame to be captured

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

    elif cmd.startswith("camcap"):
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
        _outbound.put(f"ACK:camcap exposure={exposure} gain={gain} - capturing...")
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
                _outbound.put(f"ERR:camcap failed: {err}")
            else:
                with open(CAPTURE_OUTPUT, "rb") as f:
                    img_bytes = f.read()
                encoded = base64.b64encode(img_bytes).decode("ascii")
                _outbound.put(f"IMGDATA:{encoded}")
                logger.info(f"Sending captured frame ({len(img_bytes)} bytes JPEG)")
        except subprocess.TimeoutExpired:
            _outbound.put("ERR:camcap timed out")
        except FileNotFoundError:
            _outbound.put("ERR:captured_frame.jpg not found after capture")
        except Exception as e:
            _outbound.put(f"ERR:camcap: {e}")

    elif raw.startswith(b"$"):
        shell_cmd = raw[1:].decode("utf-8", errors="replace").strip()
        logger.info(f"Shell cmd: {shell_cmd!r}")
        try:
            result = subprocess.run(
                shell_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=SHELL_CMD_TIMEOUT,
                cwd=TELEMD_DIR,
            )
            output = result.stdout + result.stderr
            if not output:
                output = f"(exit {result.returncode}, no output)"
            output = output[:CMDOUT_MAX_BYTES]
            encoded = base64.b64encode(output.encode("utf-8")).decode("ascii")
            _outbound.put(f"CMDOUT:{encoded}")
        except subprocess.TimeoutExpired:
            _outbound.put("ERR:command timed out")
        except Exception as e:
            _outbound.put(f"ERR:shell failed: {e}")

    elif raw.startswith(b"setconfig:"):
        try:
            encoded = raw[len(b"setconfig:"):]
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


def _telemetry_scheduler() -> None:
    """Send a TEL packet every second. No device access — only enqueues."""
    logger.info("Telemetry scheduler started")
    while not _shutdown.is_set():
        _shutdown.wait(1.0)
        status = _read_status()
        with _porter_lock:
            porter_running = (
                _porter_process is not None and _porter_process.poll() is None
            )
        status["porter"] = "running" if porter_running else "stopped"
        _outbound.put(f"TEL:{json.dumps(status, separators=(',', ':'))}")


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
        threading.Thread(target=_io_thread,           args=(antenna,), daemon=True),
        threading.Thread(target=_telemetry_scheduler,                  daemon=True),
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