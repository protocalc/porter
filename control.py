import datetime
import logging
import os
import signal
import sys
import threading
import time
import yaml
import argparse

from exceptions import ServiceExitError, FlagSetError
import parameters as params

from telemetry.command_server import CommandServer

# define timestamp for data saving
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# create paths
path = os.path.dirname(os.path.realpath(__file__))
data_directory = os.path.join(params.home_directory, params.data_folder_name)

# check if there are other files with same name structure
if params.INCREMENTAL_FILE_PREFIX:
    suffix = 0
    folder_list = os.listdir(data_directory)
    # parse the suffix and timestamp from the folder names
    for folder in folder_list:
        # split at _
        parts = folder.split("_")
        if len(parts) == 3:
            try:
                # check if the first part is an integer
                is_int = int(parts[0])
                # check if the second part is a valid timestamp
                datetime.datetime.strptime(parts[1] + "_" + parts[2], "%Y%m%d_%H%M%S")
                # if both checks pass, increment the suffix
                suffix += 1
            except ValueError:
                pass
    working_data_directory = os.path.join(data_directory, f"{suffix:03d}_{timestamp}")
else:
    working_data_directory = os.path.join(data_directory, timestamp)
logfile_path = os.path.join(working_data_directory, params.logfile_name)
current_symlink_path = os.path.join(data_directory, params.current_symlink_name)


# create directories if they do not exist
if not os.path.exists(data_directory):
    os.mkdir(data_directory)
if not os.path.exists(working_data_directory):
    os.mkdir(working_data_directory)

# set up logging
logging.basicConfig(
    format=params.LOGGING_FORMAT_FILE,
    datefmt=params.LOGGING_DATE_FORMAT,
    level=params.LOGGING_LEVEL,
    handlers=[
        logging.FileHandler(logfile_path),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# remove existing symlink and create a new one to the current data directory
if os.path.islink(current_symlink_path):
    os.remove(current_symlink_path)
    logger.info(f"Removed existing symlink {current_symlink_path}")
os.symlink(working_data_directory, current_symlink_path)
logger.info(f"Created symlink {current_symlink_path} -> {working_data_directory}")


# import modules that use the logger
import porter.sensors.sensors_handler as sh
import porter.threads as threads
import porter.valon as valon
from telemetry.StatusBoard import StatusBoard

# initialize the status board
status_board = StatusBoard()


def handler(signum, frame):
    logger.error(f"Caught signal {signal.strsignal(signum)}")
    raise ServiceExitError


def capture_flag(flag):
    if flag.is_set():
        logger.error(f"Flag has been set in a Thread")
        raise FlagSetError

# arg parser for command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config_file", type=str, help="Path to the config file", default="config/default.yml")


def main():
    logger.info("Starting main program...")
    args = parser.parse_args()
    config_file = args.config_file

    # global flags
    shutdown_flag = threading.Event()
    autostart_camera_flag = True
    autostart_poi_tracking_flag = True

    owned_threads = []  # track only threads we start ourselves

    # opening config file
    config_path = f"{path}/{config_file}"
    with open(config_path, "r") as cfg:
        config = yaml.safe_load(cfg)
        logger.info(f"Loaded configuration {config_file}")
    
    # saving a copy of the config file in the data directory
    config_path_copy = f"{working_data_directory}/{config_file.split('/')[-1]}"
    with open(config_path_copy, "w") as cfg:
        yaml.dump(config, cfg)
        logger.info(f"Saved configuration {config_file} copy to {config_path_copy}")

    # define paths for sensors and camera data
    sensor_path = f"{working_data_directory}/{params.sensors_folder_name}/"
    camera_path = f"{working_data_directory}/{params.camera_folder_name}/"
    if not os.path.exists(sensor_path):
        os.mkdir(sensor_path)
    if not os.path.exists(camera_path):
        os.mkdir(camera_path)

    # set up signal handlers
    for sig in params.signal_to_catch:
        signal.signal(sig, handler)

    time.sleep(1)

    try:
        global_config = config.get("global", {})
        sensors = config.get("sensors", None)
        source = config.get("source", None)
        camera = config.get("camera", None)
        pointing_controller = config.get("pointing_controller", None)

        # check for global configuration autostart parameters
        if global_config:
            logger.info(f"Found global configuration parameters")
            autostart_camera_flag       = global_config.get("autostart_camera",       True)
            autostart_poi_tracking_flag = global_config.get("autostart_poi_tracking", True)
            if autostart_camera_flag:
                logger.info(f"Global config: autostart_camera is enabled")
            else:
                logger.info(f"Global config: autostart_camera is disabled")
            if autostart_poi_tracking_flag:
                logger.info(f"Global config: autostart_poi_tracking is enabled")
            else:
                logger.info(f"Global config: autostart_poi_tracking is disabled")

        # start the StatusWriter thread
        # (telemd.py owns the XBee and reads the file written here)
        cmd_server = None
        logger.info(f"Found status writer key in config")
        update_rate = 1.0/params.STATUS_WRITER_UPDATE_RATE
        t = threads.StatusWriter(
            status_board=status_board,
            update_rate=update_rate,
            flag=shutdown_flag,
            daemon=False,
        )
        t.start()
        owned_threads.append(t)
        logger.info(f"StatusWriter started at {update_rate} Hz")

        # start command server thread for handling commands from remote telemetry clients
        cmd_server = CommandServer(shutdown_flag=shutdown_flag)

        # start sensor threads if sensors are configured
        if sensors is not None:
            logger.info(f"Found sensor key in config")

            logger.info("Starting sensor threads...")
            sensor_names = {}
            sensor_handler = {}
            sensor_threads = {}

            for i in sensors.keys():
                logger.info(f"Initializing sensor {i}")
                sensors_handler = sh.Handler(sensors[i])

                name = sensors[i]["name"]
                sensor_handler[name] = sensors_handler
                sensor_names[name] = name

            for i in sensor_handler.keys():
                logger.info(f"Starting thread for sensor {i}")
                t = threads.Sensors(
                    handler=sensor_handler[i],
                    flag=shutdown_flag,
                    date=timestamp,
                    path=sensor_path,
                    sensor_name=sensor_names[i],
                    status_board=status_board,
                    daemon=False,
                )
                t.start()
                owned_threads.append(t)
                sensor_threads[i] = t
                logger.info(f"Thread started for sensor {i}")

        # get the onboard gnss source if configured
        gnss_source = None
        if sensors is not None:
            for i in sensors.keys():
                if i.lower().startswith("gps"):
                    name = sensors[i]["name"]
                    gps_thread = sensor_threads.get(name)
                    if gps_thread is not None and gps_thread.ready.wait(timeout=params.SENSOR_INIT_TIMEOUT) and hasattr(gps_thread.handler, "obj"):
                        gnss_source = gps_thread.handler.obj.get_gnss_source()
                        logger.info(f"GNSS source initialized from GPS sensor")
                    else:
                        logger.error(f"GPS sensor {name} did not initialize in time, no GNSS source available")
                    break

        # start Valon synthesizer if source is configured
        if source is not None:
            logger.info(f"Found source key in config")

            logger.info(f"Starting Valon synthesizer on port {source['port']} and baudrate {source['baudrate']}")
            synt = valon.Valon(source["port"], source["baudrate"])
            
            logger.info(f"Setting Valon frequency to {source['freq'] / source['mult_factor']} Hz and power to {source['power']} dBm")
            synt.set_freq(source["freq"] / source["mult_factor"])
            synt.set_pwr(source["power"])

            if source["mod_freq"] > 0:
                logger.info(f"Setting Valon modulation frequency to {source['mod_freq']} Hz and amplitude to {source['mod_amp']}")
                synt.set_amd(source["mod_amp"], source["mod_freq"])
            else:
                logger.info(f"Disabling Valon amplitude modulation")
                synt.set_amd(0, 0)

            attempts = params.ATTEMPTS
            valon_id = None
            for i in range(attempts):
                logger.info(f"Attempt {i+1}/{attempts} to get Valon ID...")
                valon_id = synt.get_id()
                time.sleep(0.01)

                if valon_id is not None:
                    break
            if valon_id is None:
                logger.error("Failed to get Valon ID after multiple attempts.")
                # raise Exception?
            else:
                logger.info(f"Valon synthesizer initialized with ID: {valon_id}")

            time.sleep(2)

        # start camera thread if camera is configured
        if camera is not None:
            logger.info(f"Found camera key in config")
            try:
                if camera["name"] == 'Alvium_Starspec':
                    t = threads.AlviumCameraStarspec(
                        camera_config=camera,
                        flag=shutdown_flag,
                        path=camera_path,
                        status_board=status_board,
                        daemon=False,
                    )
                    t.start()
                    owned_threads.append(t)
                    logger.info(f"Thread started for camera {camera['name']}")
                elif camera["name"] == 'Alvium':
                    t = threads.AlviumCamera(
                        camera_config=camera,
                        flag=shutdown_flag,
                        path=camera_path,
                        status_board=status_board,
                        daemon=False,
                    )
                    cmd_server.register("camera.start", t.start)
                    if autostart_camera_flag:
                        t.start()
                    owned_threads.append(t)
                    logger.info(f"Thread started for camera {camera['name']}")
                elif camera["name"] == 'Sony':
                    t = threads.SonyCamera(
                        camera_config=camera,
                        flag=shutdown_flag,
                        daemon=True,
                    )
                    t.start()
                    owned_threads.append(t)
                    logger.info(f"Thread started for camera {camera['name']}")
                else:
                    logger.error(f"Unknown camera name: {camera['name']}")
                    shutdown_flag.set()

                time.sleep(2)

            except IndexError:
                shutdown_flag.set()

        # start pointing controller threads and pass configuration file
        if pointing_controller is not None:
            logger.info(f"Found pointing controller key in config")
            if pointing_controller["name"] == 'lager':
                t = threads.PointingController(
                    pointing_controller_config=pointing_controller,
                    path=working_data_directory,
                    flag=shutdown_flag,
                    status_board=status_board,
                    gnss_source=gnss_source,
                    daemon=False,
                )
                t.start()
                logger.info(f"Registering POI tracking commands for pointing controller {pointing_controller['name']} with command server...")
                cmd_server.register("gimbal.starttrack", t.start_tracking)
                cmd_server.register("gimbal.stoptrack", t.stop_tracking)
                if autostart_poi_tracking_flag:
                    t.start_tracking()
                owned_threads.append(t)
                logger.info(f"Thread started for pointing controller {pointing_controller['name']}")

                # register commands for gimbal control with the command server, retrying if necessary
                # due to serial connection latency and protocol initialization time
                if cmd_server is not None:
                    attempts = params.ATTEMPTS
                    while attempts > 0:
                        try:
                            logger.info(f"Registering gimbal commands for pointing controller {pointing_controller['name']} with command server... attempt {params.ATTEMPTS - attempts + 1}/{params.ATTEMPTS}")
                            cmd_server.register("gimbal.goto", t.pc.gimbal.goto)
                            cmd_server.register("gimbal.mode", t.pc.gimbal.set_mode)
                            attempts = 0  # exit loop if successful
                        except Exception as e:
                            logger.error(f"Error registering commands for pointing controller {pointing_controller['name']}: {e}")
                        attempts -= 1
                        time.sleep(1)

        # start command server thread for handling commands from remote telemetry clients
        if cmd_server is not None:
            cmd_server.start()

        while not shutdown_flag.is_set():
            time.sleep(0.2)

    except (ServiceExitError, FlagSetError) as err:
        logger.error(f"Exception occurred: {err.__class__.__name__}")
        shutdown_flag.set()

    # reset signal handlers to default
    for sig in params.signal_to_catch:
        signal.signal(sig, signal.SIG_DFL)

    logger.info("Waiting for threads to finish...")
    time.sleep(0.5)
    for thread in owned_threads:
        if not thread.is_alive():
            logger.info(f"Thread {thread.name} already finished.")
            continue
        logger.info(f"Joining thread {thread.name}...")
        thread.join(timeout=params.THREAD_JOIN_TIMEOUT)
        if thread.is_alive():
            logger.warning(f"Thread {thread.name} did not finish in time and is still alive.")
        else:
            logger.info(f"Thread {thread.name} has finished.")

if __name__ == "__main__":
    main()
