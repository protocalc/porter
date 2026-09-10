# power_monitor

**Not implemented yet.** This folder contains draft code for a battery power-monitoring daemon; it is not integrated into the flight software or deployed on the payload.

- **`powerd.py`** — draft standalone daemon intended to own an INA228 power monitor: poll bus voltage/current/power/temperature/energy once per second, check them against fixed over/under-voltage and over-current thresholds, and write the result to a JSON status file (`/tmp/powerd_status.json`) for other processes to read.
- **`ina228.py`** — draft INA228 I2C driver used by `powerd.py`.

There is a `powerd.service` unit under `startup/` for eventually running this as a systemd service, but until this module is finished, tested against real hardware, and wired into the rest of PORTER (e.g. `telemetry/telemd.py`, which currently expects a different status-file path than the one `powerd.py` writes), it should be treated as work in progress rather than part of the current flight software.

See the repository root [README.md](../README.md) for the overall PORTER architecture.
