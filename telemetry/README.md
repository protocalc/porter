# telemetry

Ground-link subsystem for PORTER: the daemon that owns the payload's XBee radio, the command/status protocol it speaks, and the client that runs on the ground laptop.

- **`telemd.py`** — systemd service (`startup/telemd.service`) that owns the XBee radio. Periodically sends payload status (`TEL:<json>`, sourced from `/tmp/porter_status.json`, written by `control.py`) to the ground, and handles incoming commands: `ping`, `reboot`, `shutdown`, `start`/`stop` (launches/stops the `control.py` subprocess), `getlog`, `setconfig <path>`, `camera.start`, `camera.capture`, `gimbal.goto`/`mode`/`starttrack`/`stoptrack`, and arbitrary background shell commands (`$<cmd>`, `jobs`, `canceljob <id>`). Camera/gimbal commands are relayed to the running `control.py` process over the `CommandServer` Unix socket.
- **`command_server.py`** — Unix-socket (`/tmp/porter_cmd.sock`) command server run inside `control.py`, used to route live commands (camera/gimbal) from `telemd.py` to the threads `control.py` owns.
- **`Xbee.py`** — low-level wrapper around the `digi-xbee` library for sending/receiving packets over the radio.
- **`StatusBoard.py`** — thread-safe heartbeat tracker; sensor/camera threads call `beat(name)` and `telemd.py`/`remote_host.py` read it to report per-sensor health (`ok`/`stale`/`dead`).
- **`alvium_capture.py`** — standalone helper script to capture a single Alvium frame, invoked by `telemd.py`'s `camera.capture` command.
- **`remote_host.py`** — `curses`-based TUI meant to run on the ground laptop (`python3 remote_host.py [--port /dev/ttyUSB0] [--baudrate 38400] [--debug]`); shows live telemetry and a command prompt using the same command set `telemd.py` accepts.
- **`default.yml`** — configuration consumed here; currently byte-for-byte identical to `config/default.yml` at the repo root.

See the repository root [README.md](../README.md) for the full PORTER architecture and how this daemon fits with `control.py` and `power_monitor/powerd.py`.
