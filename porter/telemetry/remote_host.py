#!/usr/bin/env python3
"""
remote_host.py  -  ground-station TUI.

Run on the laptop.  Shows live telemetry from porter (via TEL packets) in the
upper panel, and a command prompt in the lower panel.

Usage:
  python3 remote_host.py [--port /dev/ttyUSB0] [--baudrate 38400]

Commands:
  ping              payload replies "pong" with RSSI
  reboot            reboot the payload computer
  shutdown          shut down the payload computer
  getlog            download last 4 KB of flight.log (base64-encoded)
  setconfig <path>  upload config file to payload
  start             start control.py on the payload
  stop              stop control.py on the payload
  help              list commands
  quit / q          exit
"""

import argparse
import base64
import curses
import json
import os
import queue
import sys
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from digi.xbee.exception import TimeoutException
from porter.telemetry.Xbee import Xbee, END_OF_MESSAGE_BYTE

# configuration
DEFAULT_PORT     = "/dev/ttyUSB0"
DEFAULT_BAUDRATE = 38400
PAYLOAD_NAME     = "LUKE"
READ_TIMEOUT     = 0.2

COMMANDS = {
    "ping":      "Check link (replies pong + RSSI)",
    "reboot":    "Reboot payload computer",
    "shutdown":  "Shut down payload computer",
    "start":     "Start control.py on payload",
    "stop":      "Stop control.py on payload",
    "getlog":    "Download last 4 KB of flight.log",
    "setconfig": "Upload config file  →  setconfig <local_path>",
    "$<cmd>":    "Run shell command on payload  e.g. $ls -la",
    "camcap":    "Capture frame  e.g. camcap -e 10000 -g 30.0 - very slow data transfer",
}

# shared state
_shutdown  = threading.Event()
_outbound: "queue.Queue[str]" = queue.Queue()

_state_lock = threading.Lock()
_tel        = {}          # latest parsed TEL payload
_rssi       = None        # downlink RSSI (dBm)
_log        = []          # recent message log
LOG_MAX     = 40


def _push_log(msg: str) -> None:
    with _state_lock:
        _log.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
        if len(_log) > LOG_MAX:
            _log.pop(0)


# XBee I/O thread
def _io_thread(antenna: Xbee) -> None:
    global _rssi
    rx_buf = b""

    while not _shutdown.is_set():

        while True:
            try:
                msg = _outbound.get_nowait()
            except queue.Empty:
                break
            try:
                antenna.send_msg(msg)
                display = msg if len(msg) <= 60 else msg[:60] + "…"
                _push_log(f"→ {display}")
            except Exception as e:
                _push_log(f"[send error] {e}")

        try:
            frame = antenna.device.read_data(timeout=READ_TIMEOUT)
        except TimeoutException:
            frame = None
        except Exception as e:
            if not _shutdown.is_set():
                _push_log(f"[read error] {e}")
            frame = None

        if frame is not None:
            rx_buf += frame.data
            if rx_buf.endswith(END_OF_MESSAGE_BYTE):
                _on_message(rx_buf[:-1], antenna)
                rx_buf = b""
            elif len(rx_buf) > 80 * 1024:
                _push_log("[rx overflow, discarding]")
                rx_buf = b""


def _on_message(raw: bytes, antenna: Xbee) -> None:
    global _rssi
    text = raw.decode("utf-8", errors="replace").strip()

    if text.startswith("TEL:"):
        try:
            payload = json.loads(text[4:])
            # read downlink RSSI from the XBee hardware register
            try:
                db = antenna.device.get_parameter("DB")
                with _state_lock:
                    _rssi = -int.from_bytes(db, byteorder="big")
            except Exception:
                pass
            with _state_lock:
                _tel.clear()
                _tel.update(payload)
        except json.JSONDecodeError as e:
            _push_log(f"[TEL parse error] {e}")

    elif text.startswith("LOGDATA:"):
        try:
            data = base64.b64decode(text[8:])
            fname = f"flight.log"
            with open(fname, "wb") as f:
                f.write(data)
            _push_log(f"← log saved → {fname} ({len(data)} bytes)")
        except Exception as e:
            _push_log(f"[LOGDATA decode error] {e}")

    elif text.startswith("CMDOUT:"):
        try:
            output = base64.b64decode(text[7:]).decode("utf-8", errors="replace")
            lines = output.splitlines()
            if not lines:
                lines = ["(empty output)"]
            for line in lines:
                _push_log(f"  {line}")
        except Exception as e:
            _push_log(f"[CMDOUT decode error] {e}")

    elif text.startswith("IMGDATA:"):
        try:
            img_bytes = base64.b64decode(text[8:])
            fname = f"captured_frame.jpg"
            with open(fname, "wb") as f:
                f.write(img_bytes)
            _push_log(f"← image saved → {fname} ({len(img_bytes) / 1024:.1f} KB)")
        except Exception as e:
            _push_log(f"[IMGDATA decode error] {e}")

    else:
        _push_log(f"← {text}")


# curses TUI
def _init_colors() -> None:
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN,  -1)   # ok
    curses.init_pair(2, curses.COLOR_YELLOW, -1)   # stale
    curses.init_pair(3, curses.COLOR_RED,    -1)   # dead / error
    curses.init_pair(4, curses.COLOR_CYAN,   -1)   # header / label
    curses.init_pair(5, curses.COLOR_WHITE,  -1)   # normal


C_OK     = lambda: curses.color_pair(1) | curses.A_BOLD
C_STALE  = lambda: curses.color_pair(2) | curses.A_BOLD
C_DEAD   = lambda: curses.color_pair(3) | curses.A_BOLD
C_HEADER = lambda: curses.color_pair(4) | curses.A_BOLD
C_NORMAL = lambda: curses.color_pair(5)
C_DIM    = lambda: curses.color_pair(5) | curses.A_DIM


def _state_attr(state: str) -> int:
    if state == "ok":    return C_OK()
    if state == "stale": return C_STALE()
    return C_DEAD()


def _safe_addstr(win, y: int, x: int, text: str, attr: int = 0) -> int:
    """Write text clipped to the window width. Returns next y."""
    h, w = win.getmaxyx()
    if y >= h - 1:
        return y
    text = text[: w - x - 1]
    try:
        win.addstr(y, x, text, attr)
    except curses.error:
        pass
    return y + 1


def _draw(stdscr, input_buf: str) -> None:
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    with _state_lock:
        tel  = dict(_tel)
        rssi = _rssi
        log  = list(_log)

    row = 0

    # header 
    title = " PORTER GROUND STATION "
    row = _safe_addstr(stdscr, row, 0, title.center(w, "═"), C_HEADER())

    system = tel.get("system", {})
    if system:
        t     = system.get("time")
        tstr  = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t)) if t else "-"
        free  = system.get("hddfree", 0)
        total = system.get("hddtot", 1)
        pct   = free / total * 100 if total else 0
        row = _safe_addstr(stdscr, row, 2,
            f"Time: {tstr}   Disk: {free:.1f}/{total:.1f} GiB ({pct:.0f}%)", C_NORMAL())
    rssi_str = f"{rssi} dBm" if rssi is not None else "-"
    porter   = tel.get("porter", "-")
    porter_attr = C_OK() if porter == "running" else (C_STALE() if porter == "stopped" else C_DEAD())
    row = _safe_addstr(stdscr, row, 2, f"Downlink RSSI: {rssi_str}   Porter: ", C_NORMAL())
    row -= 1  # stay on same row
    x_porter = 2 + len(f"Downlink RSSI: {rssi_str}   Porter: ")
    _safe_addstr(stdscr, row, x_porter, porter.upper(), porter_attr)
    row += 1

    # health
    row = _safe_addstr(stdscr, row, 0, "─" * w, C_DIM())
    row = _safe_addstr(stdscr, row, 2, "HEALTH", C_HEADER())

    health = tel.get("health", {})
    meta   = tel.get("meta", {})
    for name, info in health.items():
        if row >= h - 6:
            break
        state = info.get("state", "?") if isinstance(info, dict) else str(info)
        age   = info.get("age_s", "") if isinstance(info, dict) else ""
        age_s = f"  {age}s" if age != "" else ""
        m     = meta.get(name, {})
        meta_s = "  " + "  ".join(f"{k}={v}" for k, v in m.items()) if m else ""
        label = f"  {name:<20}"
        row = _safe_addstr(stdscr, row, 0, label, C_NORMAL())
        row -= 1
        _safe_addstr(stdscr, row, len(label), f"[{state}]", _state_attr(state))
        rest = f"{age_s}{meta_s}"
        _safe_addstr(stdscr, row, len(label) + len(f"[{state}]"), rest, C_DIM())
        row += 1

    # log
    row = _safe_addstr(stdscr, row, 0, "─" * w, C_DIM())
    row = _safe_addstr(stdscr, row, 2, "LOG", C_HEADER())

    log_rows = h - row - 3   # leave 3 rows for prompt
    visible  = log[-log_rows:] if log_rows > 0 else []
    for line in visible:
        attr = C_OK() if "← pong" in line or "← ACK" in line else \
               C_DEAD() if "← ERR" in line or "[error]" in line else C_NORMAL()
        row = _safe_addstr(stdscr, row, 2, line, attr)

    # command prompt
    prompt_row = h - 2
    _safe_addstr(stdscr, prompt_row - 1, 0, "─" * w, C_DIM())
    _safe_addstr(stdscr, prompt_row, 0,
                 f"  cmd> {input_buf}", C_NORMAL())

    stdscr.move(prompt_row, 7 + len(input_buf))
    stdscr.refresh()


def _tui(stdscr, antenna: Xbee) -> None:
    _init_colors()
    curses.curs_set(1)
    stdscr.keypad(True)
    stdscr.timeout(300)   # non-blocking getch with 300 ms timeout

    input_buf = ""

    while not _shutdown.is_set():
        _draw(stdscr, input_buf)

        ch = stdscr.getch()
        if ch == -1:
            continue

        if ch in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            original_input = input_buf.strip()
            cmd = original_input.lower()
            input_buf = ""
            if cmd in ("quit", "exit", "q"):
                _shutdown.set()
                break
            elif cmd == "help":
                _push_log("Available commands:")
                for c, desc in COMMANDS.items():
                    _push_log(f"  {c:<12} {desc}")
            elif cmd == "getlog":
                _outbound.put("getlog")
            elif original_input.startswith("$"):
                _outbound.put(original_input)
            elif cmd.startswith("camcap"):
                _outbound.put(original_input)
            elif cmd.startswith("setconfig"):
                parts = original_input.split(None, 1)  # preserve original case for path
                if len(parts) < 2:
                    _push_log("Usage: setconfig <local_path>")
                else:
                    path = parts[1].strip()
                    try:
                        with open(path, "rb") as fh:
                            raw_yml = fh.read()
                        encoded = base64.b64encode(raw_yml).decode("ascii")
                        _outbound.put(f"setconfig:{encoded}")
                        _push_log(f"→ setconfig ({len(raw_yml)} bytes from {path})")
                    except FileNotFoundError:
                        _push_log(f"ERR: file not found: {path}")
                    except Exception as e:
                        _push_log(f"ERR: {e}")
            elif cmd in COMMANDS:
                _outbound.put(cmd)
            elif cmd:
                _push_log(f"Unknown command '{cmd}'. Type 'help'.")

        elif ch in (curses.KEY_BACKSPACE, 127, 8):
            input_buf = input_buf[:-1]

        elif 32 <= ch < 127:
            input_buf += chr(ch)


# main
def main() -> None:
    parser = argparse.ArgumentParser(description="Porter ground station")
    parser.add_argument("--port",     default=DEFAULT_PORT,    help="Local XBee serial port")
    parser.add_argument("--baudrate", default=DEFAULT_BAUDRATE, type=int)
    args = parser.parse_args()

    print(f"Connecting to {args.port} @ {args.baudrate} baud ...")
    antenna = Xbee(port=args.port, baudrate=args.baudrate)
    antenna.open(force_settings=True, remote_name=PAYLOAD_NAME)
    print(f"Connected. Remote: {antenna.remote_device}\nStarting TUI...")
    time.sleep(0.5)

    t = threading.Thread(target=_io_thread, args=(antenna,), daemon=True)
    t.start()

    try:
        curses.wrapper(_tui, antenna)
    finally:
        _shutdown.set()
        print("Closing XBee...")
        try:
            antenna.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()