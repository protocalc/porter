# PORTER

PORTER is the main flight/control software for the **POLOCALC** drone-based payload project. It runs on the payload's onboard computer (currently a Raspberry Pi 5, `RPi5_dev` branch — porter version `4.0`) and is responsible for:

- reading out the payload's sensors (GPS, IMU/inertial, ADC, temperature) and writing their raw data to disk,
- driving the science camera (Vimba/Alvium industrial camera, or a Sony camera via the `sour_core` module),
- controlling a Valon RF synthesizer used as a signal source,
- driving a stabilized gimbal (via the `lager` module) for autonomous point-of-interest (POI) tracking, using either the payload's own GNSS fix or a drone's DRTK position,
- exposing a lightweight command/telemetry link to the ground over an XBee radio, and
- monitoring battery power (bus voltage/current/temperature) via an INA228 power monitor.

The same `control.py` entry point, driven by a YAML configuration file, is reused across the different phases of the project (bench testing, integration, flight) simply by swapping the configuration.

## Repository Structure

```
porter/
├── control.py              # main flight-software entry point (see Usage)
├── parameters.py            # global constants (paths, timeouts, logging format, signals)
├── exceptions.py             # ServiceExitError / FlagSetError used for clean shutdown
├── config/
│   └── default.yml           # sensor/camera/gimbal configuration consumed by control.py
├── porter/
│   ├── threads.py            # threading.Thread subclasses: Sensors, cameras, PointingController, StatusWriter
│   ├── valon.py               # serial driver for the Valon RF synthesizer
│   └── sensors/               # Python wrappers around each sensor (see Sensors supported)
├── telemetry/
│   ├── telemd.py              # XBee ground-link daemon (systemd service)
│   ├── command_server.py       # Unix-socket command server used by control.py to expose live commands
│   ├── remote_host.py          # curses ground-station TUI client (runs on the ground laptop)
│   ├── StatusBoard.py          # thread-safe sensor/camera heartbeat tracker
│   ├── Xbee.py                 # low-level XBee device wrapper (digi-xbee)
│   ├── alvium_capture.py        # standalone helper: capture a single Alvium frame (used by telemd's camera.capture command)
│   └── default.yml              # currently byte-for-byte identical to config/default.yml
├── power_monitor/
│   ├── powerd.py                # INA228 battery-monitoring daemon (systemd service)
│   └── ina228.py                 # INA228 driver (adafruit-circuitpython-ina228)
├── decoders/                   # offline, standalone scripts to decode/plot the binary data recorded by control.py
│   ├── ads1x15.py, ads1x15_LB.py, ads1x15_TS.py, ads1x15_starspec.py
│   ├── inertial.py
│   ├── kernel.py
│   └── ubx.py
├── startup/
│   ├── telemd.service, powerd.service   # systemd unit files (see Deployment)
│   ├── i2c-config.service                 # oneshot systemd unit running i2c_startup_config.sh at boot
│   └── i2c_startup_config.sh                # sets the CPU frequency governor to "performance" on cores 0-3
├── bin/                        # pre-built ARM64 (aarch64) binaries invoked by the sensor/camera Python wrappers
│   ├── ads1015, inertial, IMX5SensorModule, LM76SensorModule, alvium
├── test/                       # older/experimental scripts (test.py, test_gps.py)
├── modules/                    # git submodules (build/vendor code — see below); not covered in depth here
├── install_modules.py          # installs Python deps + submodules + builds the bin/ binaries + installs systemd services
├── setup_gps.py, startup_nmea.py, startup_script.sh   # standalone GPS bring-up helpers (see Usage)
├── version_history.txt         # plain-text changelog, V2.0 → current V4.0
└── LICENSE                     # MIT
```

## Requirements / Dependencies

- **Hardware**: Raspberry Pi 5 (current target; `RPi5_dev` branch) with I2C/UART/USB-connected sensors, an XBee radio for the ground link, and (optionally) a Valon synthesizer, Gremsy gimbal, and Alvium/Sony camera.
- **Python** 3, with packages including `pyyaml`, `pyserial`, `pyubx2`/`pynmeagps`, `digi-xbee`, `adafruit-circuitpython-ina228`, `adafruit-circuitpython-mcp4725`, `pyusb`, plus the project's own submodules (`vmbpy`, `pyalvium`, `lager`, `sour_core`) — all installed by `install_modules.py`.
- **Compiled sensor binaries** in `bin/` — pre-built `aarch64` ELF executables (the wrapper classes in `porter/sensors/` shell out to these via `subprocess`). They are built from the `ADS1015-ADC-Module`, `Inertial-Sensors-Module`, `LM76-Temperature-Sensor`, `IMX-5-Sensor-Module`, and `Alvium-Camera-Module` submodules.
- A dedicated Python virtual environment is expected at `/home/polocalc/porter_venv` (referenced by `telemd.py` and the `startup/*.service` files) and the payload's home directory is assumed to be `/home/polocalc` (`parameters.home_directory`).

## Installation

1. Clone the repository together with its submodules (`modules/IMX-5-Sensor-Module`, `Alvium-Camera-Module`, `Alvium-Camera-Module-Python`, `Inertial-Sensors-Module`, `LM76-Temperature-Sensor`, `ADS1015-ADC-Module`, `lager`, `sour_core` — see `.gitmodules`), e.g. `git clone --recurse-submodules ...`.
2. Run `python3 install_modules.py` from the repo root. It:
   - `pip install`s `vmbpy`, `pyalvium` (editable, from `modules/Alvium-Camera-Module-Python`), `digi-xbee==1.5.0`, `adafruit-circuitpython-ina228`, `pyubx2`, `adafruit-circuitpython-mcp4725`, `pyusb`, `pyyaml`,
   - installs `lager` and `sour_core` in editable mode from `modules/`,
   - builds the Rust-based `ADS1015-ADC-Module`, `Inertial-Sensors-Module`, and `LM76-Temperature-Sensor` submodules via each one's `build_for_pi.sh` (their build output is expected to land in `bin/`),
   - copies `startup/telemd.service` and `startup/powerd.service` into `/etc/systemd/system/`, reloads systemd, and enables + starts both services.
3. The `Alvium-Camera-Module` and `IMX-5-Sensor-Module` binaries (`bin/alvium`, `bin/IMX5SensorModule`) are not built by `install_modules.py` in the current script and must be built separately from their own submodule directories.

Per project convention, `modules/` submodules are developed and fixed in their own upstream repositories — this README does not document their internals beyond the one-line summaries below.

| Submodule | Purpose |
|---|---|
| `ADS1015-ADC-Module` | Rust implementation for configuring/reading the ADS1015 ADC for data logging. |
| `Alvium-Camera-Module` | C/C++ implementation for configuring/handling the Alvium camera for data logging (compiled to `bin/alvium`). |
| `Alvium-Camera-Module-Python` | Python module (`pyalvium`) controlling the Alvium camera via `vmbpy`, with parallelized frame writing to NVMe. |
| `IMX-5-Sensor-Module` | C++ project using the Inertial Sense SDK to read the IMX-5 IMU/INS sensor. |
| `Inertial-Sensors-Module` | Rust implementation for the legacy inertial sensors (IMU, magnetometer, barometer). |
| `LM76-Temperature-Sensor` | Rust driver for the TI LM76 I2C temperature sensor. |
| `lager` | "Live Attitude and Gimbal Error Resolver" — Python controller coordinating a drone (DJI M600) and a Gremsy T7 gimbal for autonomous POI tracking. |
| `sour_core` | Shared core code (e.g. Sony camera control) used by both `porter` and the separate `SOUR` GUI project. |

## Configuration

`control.py` loads a single YAML file (default `config/default.yml`, overridable with `-c/--config_file`). Top-level keys, based on the current `config/default.yml`:

- **`global`**: `name`, `version`, `description`, plus autostart flags `autostart_camera` and `autostart_poi_tracking` (both read by `control.py` to decide whether to start the camera/POI-tracking threads immediately or wait for a remote command).
- **`sensors`**: a mapping of arbitrary sensor keys (e.g. `GPS_1`, `ADC_1`, `IMX5_1`, `DAC_1`, `INERTIAL_1`) each with `name`, optional `sensor_core` (CPU core pinning passed to the compiled binaries), `connection` (`type`: `serial` or `I2C`, plus its parameters), `sensor_info` (`type`/`manufacturer`, used by `porter/sensors/sensors_handler.py` to pick the right driver class), and a driver-specific `configuration` block. The current default config enables a UBlox ZED-F9P GPS, an ADS1015 ADC, an IMX5-Sensors IMU/INS, an MCP4725 DAC, and a generic "Inertial" sensor (legacy IMU/magnetometer/barometer, manufacturer "Varios").
- **`camera`**: `name` (`Alvium`, `Alvium_Starspec`, or `Sony` — dispatched in `porter/threads.py`), plus camera-specific settings (`exposure`, `gain`, `format`, `max_framerate`, `writing_threads`, `verbosity`, ROI, etc.).
- **`pointing_controller`**: `name: lager`, a `gimbal` block (name, serial connection, mavlink protocol, telemetry rates) and a `poi` block (target latitude/longitude/altitude and `max_distance`) consumed by the `lager` module.
- **`status_writer`**: `enabled`/`update_rate` keys are present in the file, though the current `control.py` always starts the `StatusWriter` thread (rate comes from `parameters.STATUS_WRITER_UPDATE_RATE`, not this block).
- **`power_monitor`**: present but commented out in the current `config/default.yml` — power monitoring instead runs as the fully independent `powerd.py` daemon (see below), not as a `control.py`-managed sensor.

`telemetry/default.yml` currently has byte-identical content to `config/default.yml`.

`parameters.py` holds constants not meant to change per run: logging format/level, retry `ATTEMPTS`, signals to catch (`SIGINT`, `SIGTERM`), `THREAD_JOIN_TIMEOUT`, `SENSOR_INIT_TIMEOUT`, `STATUS_WRITER_UPDATE_RATE`, and path/naming conventions for the data directory (`home_directory = "/home/polocalc"`, `data_folder_name = "data"`, `sensors_folder_name`, `camera_folder_name`, `current_symlink_name = "current"`, `logfile_name = "flight.log"`), plus `INCREMENTAL_FILE_PREFIX` which, when `True`, prefixes each run's data folder with an incrementing 3-digit counter (e.g. `001_20260910_101500`).

## Usage

### Main flight software — `control.py`

```
python3 control.py [-c/--config_file CONFIG_FILE]
```

- `-c`/`--config_file` — path to the YAML config, relative to the repo root (default: `config/default.yml`).
- On startup it creates a timestamped (optionally incrementally-numbered) run directory under `<home_directory>/data/`, symlinks it as `<home_directory>/data/current`, saves a copy of the config file used, and logs to `<run_dir>/flight.log` and stdout.
- It then, in order: starts a `StatusWriter` thread (writes `/tmp/porter_status.json` at 1 Hz for `telemd.py` to pick up), starts a `CommandServer` (Unix socket `/tmp/porter_cmd.sock`) so remote commands can reach running threads, starts one `Sensors` thread per configured sensor, locates a GNSS source from the first `GPS*`-keyed sensor (if any), configures the Valon synthesizer if a `source` block is present, starts the configured camera thread, and starts the `PointingController` thread (registering `gimbal.goto`, `gimbal.mode`, `gimbal.starttrack`, `gimbal.stoptrack` commands with the command server).
- It runs until `SIGINT`/`SIGTERM` (or an internal `ServiceExitError`/`FlagSetError`) is raised, then joins all owned threads (with a timeout) before exiting.
- `control.py` is normally started/stopped remotely via `telemd.py`'s `start`/`stop` commands (which invoke it inside `/home/polocalc/porter_venv`), not run directly in production.

### Telemetry / ground-link daemon — `telemetry/telemd.py`

Runs continuously as a systemd service (`telemd.service`) and owns the XBee radio. It reads `/tmp/porter_status.json` (written by `control.py`'s `StatusWriter`) and `/tmp/power_cmd.json` (expected from `powerd.py`) and periodically sends a `TEL:<json>` packet to the ground station. It accepts commands from the ground over XBee, including:

`ping`, `reboot`, `shutdown`, `start`, `stop`, `getlog`, `setconfig <path>`, `camera.start`, `camera.capture [-e <exposure>] [-g <gain>]`, `gimbal.goto <yaw> <pitch> <roll>`, `gimbal.mode <mode>`, `gimbal.starttrack`, `gimbal.stoptrack`, `$<shell command>` (background job with `jobs`/`canceljob <id>` management), and unrecognized commands get an `ERR:` reply.

Camera/gimbal commands are relayed to the running `control.py` process over the `CommandServer` Unix socket (`/tmp/porter_cmd.sock`); `start`/`stop` launch or signal the `control.py` subprocess directly.

### Ground station — `telemetry/remote_host.py`

A `curses`-based TUI meant to run on the ground laptop:

```
python3 remote_host.py [--port /dev/ttyUSB0] [--baudrate 38400] [--debug]
```

It shows live telemetry (disk usage, porter/chrony/power-controller status, per-sensor health from the `StatusBoard`) in the upper panel and a command prompt (same command set as `telemd.py` above) in the lower panel.

### Power daemon — `power_monitor/powerd.py`

Runs continuously as a systemd service (`powerd.service`), independent of `control.py`. A single thread polls the INA228 power monitor once per second and atomically writes bus voltage/current/power/temperature/energy plus derived over/under-voltage and over-current alarm flags to `/tmp/powerd_status.json`. Note: `telemd.py` currently reads power status from a differently-named path (`/tmp/power_cmd.json`, `POWER_CONTROLLER_STATUS_PATH`) than the one `powerd.py` writes to (`/tmp/powerd_status.json`).

### Standalone GPS helpers

`setup_gps.py`, `startup_nmea.py`, and `startup_script.sh` are separate from `control.py`: `startup_nmea.py` uses `pyubx2` to (re)configure the ZED-F9P's UART1 (UBX) / UART2 (NMEA) output protocols and message set directly over serial; `startup_script.sh` runs it three times with short delays (its hardcoded path `/home/polocalc/Documents/porter/startup_nmea.py` differs from the `/home/polocalc/flight/porter` path used by the systemd services, suggesting it may predate the current deployment layout). `setup_gps.py` is an older, GPS-focused variant of the main control loop that uses an earlier `Sensors`/`Handler` calling convention than the current `porter/threads.py`/`porter/sensors/sensors_handler.py`.

### Offline decoders — `decoders/`

Standalone, argparse-driven scripts (not imported by `control.py`) to parse and plot the raw `.bin` files written by the sensor threads: `ads1x15.py`/`ads1x15_LB.py`/`ads1x15_TS.py`/`ads1x15_starspec.py` for ADC data variants, `inertial.py` for the legacy inertial sensors, `kernel.py` for the (currently unused) Inertial Labs inclinometer, and `ubx.py` for GPS/UBX data.

## Sensors Supported

Dispatch happens in `porter/sensors/sensors_handler.py` based on each sensor's `sensor_info.type` (case-insensitive):

| `sensor_info.type` | Driver | Notes |
|---|---|---|
| `gps` | `porter/sensors/ubx.py` (`UBX`) | Pure-Python driver using `pyubx2`/`pynmeagps` over serial; used for the UBlox ZED-F9P in `config/default.yml`. |
| `adc` | `porter/sensors/ads1015.py` (`ADS1015`) | Shells out to the compiled `bin/ads1015` binary (I2C, configurable gain/data rate). |
| `inertial` | `porter/sensors/inertial.py` (`Inertial`) | Shells out to `bin/inertial` (I2C); IMU output is currently hardcoded disabled (`--no-imu`) per a comment in that file. This is the "legacy" IMU/magnetometer/barometer sensor, distinct from KERNEL below. |
| `dac` | `porter/sensors/mcp4725.py` (`MCP4725`) | Direct `adafruit_mcp4725` I2C driver; used to set a fixed output voltage rather than log data. |
| `inclinometer` (manufacturer `inertial_labs`) | `porter/sensors/KERNEL.py` (`KernelInertial`) | Pure-Python driver for the Inertial Labs KERNEL inclinometer. **Not referenced in the current `config/default.yml`/`telemetry/default.yml`** — supported in code but not currently used on this payload. |
| `imx5` | `porter/sensors/IMX5SensorModule.py` (`IMX5SensorModule`) | Shells out to `bin/IMX5SensorModule` (serial/USB); configurable IMU/INS data rates. |
| `lm76` | `porter/sensors/LM76SensorModule.py` (`LM76SensorModule`) | Shells out to `bin/LM76SensorModule` (I2C); optional `tcrit`/`thyst`/`tlow`/`thigh` alarm thresholds. |

All of the "shells out to a binary" drivers run their subprocess in a loop, verify the output file/directory keeps getting fresh data after a startup grace period, and call `status_board.beat(name)` each iteration so `StatusBoard`/`telemd.py`/`remote_host.py` can report per-sensor health (`ok`/`stale`/`dead`). `porter/sensors/FakeSensor.py` provides a `FakeConnection` for local development without hardware (`Handler(..., local=True)`).

## Camera & Gimbal

- **Camera** (`camera` config block, dispatched in `porter/threads.py`): `Alvium` (Python `pyalvium` module, multithreaded frame writing, started/stopped through the command server and optionally autostarted), `Alvium_Starspec` (shells out to the compiled `bin/alvium` binary), or `Sony` (via the `sour_core.sony` module, supports `video`/`photo` modes with configurable ISO/shutter speed/focus distance).
- **Pointing controller / gimbal** (`pointing_controller` config block): only `lager` is currently supported. `porter/threads.py`'s `PointingController` thread connects to the Gremsy T7 gimbal (over mavlink/serial), starts telemetry, and can autonomously track a configured point of interest (`poi`) using a GNSS source obtained from the first configured `GPS*` sensor. `gimbal.goto`, `gimbal.mode`, `gimbal.starttrack`, `gimbal.stoptrack` are exposed as remote commands.
- **Valon RF synthesizer** (`porter/valon.py`, `source` config block): serial driver to set frequency, power, and AM modulation on a Valon synthesizer, used as a signal source rather than a sensor.

## Deployment (Raspberry Pi 5)

Two long-running systemd services, installed by `install_modules.py` from `startup/`:

- **`telemd.service`** — runs `telemetry/telemd.py` in `/home/polocalc/porter_venv`, `WorkingDirectory=/home/polocalc/flight/porter`, restarts on failure, waits 5 s at start for the XBee USB device to enumerate.
- **`powerd.service`** — runs `power_monitor/powerd.py` the same way, restarts on failure, waits 5 s at start.

`control.py` itself is **not** a systemd service — it is started/stopped on demand by `telemd.py`'s `start`/`stop` commands (or manually).

A third unit, **`startup/i2c-config.service`**, is a one-shot service (`Before=zkbootrtc.service`) that runs `startup/i2c_startup_config.sh` at boot; despite the name, that script sets the CPU frequency scaling governor to `performance` on cores 0-3 rather than configuring I2C directly.

## Version / Changelog

See `version_history.txt` for the full history. The current version is:

> **V4.0 — Raspberry Pi 5 version of porter**
> - Alvium camera is handled by a Python module with multithreaded memory writing
> - XBee modules are used for line-of-sight telemetry/control
> - Integrated `lager` module for gimbal control and drone live telemetry access
> - Point-of-interest autonomous tracking using the payload's GNSS or a drone's DRTK

## License

MIT License, Copyright (c) 2021 protocalc. See `LICENSE`.
