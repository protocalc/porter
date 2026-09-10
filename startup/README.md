# startup

systemd unit files and boot-time scripts used to deploy PORTER on the payload's Raspberry Pi 5. Installed into `/etc/systemd/system/` by `install_modules.py` (currently `telemd.service` and `powerd.service` only).

- **`telemd.service`** — runs `telemetry/telemd.py` (the XBee ground-link daemon) as user `polocalc` from `/home/polocalc/flight/porter`, using the project venv at `/home/polocalc/porter_venv`. Waits 5 s at boot for the XBee USB device to enumerate, restarts on failure, logs to the journal (`journalctl -u telemd -f`).
- **`powerd.service`** — runs `power_monitor/powerd.py` (the INA228 power-monitoring daemon) the same way, restarts on failure, logs to the journal (`journalctl -u powerd -f`).
- **`i2c-config.service`** — a one-shot service, run before `zkbootrtc.service`, that executes `/usr/local/bin/i2c_startup_config.sh` at boot. Despite the name, that script does not configure I2C — it sets the CPU frequency scaling governor to `performance` on cores 0-3 (`i2c_startup_config.sh` must be copied to `/usr/local/bin/` separately, as `install_modules.py` does not do this).

`control.py` itself is **not** deployed as a systemd service — it is started and stopped on demand by `telemd.py`'s `start`/`stop` commands over the XBee link (or run manually).

See the repository root [README.md](../README.md) for the full PORTER architecture.
