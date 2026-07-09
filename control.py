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

# define timestamp for data saving
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# create paths
path = os.path.dirname(os.path.realpath(__file__))
home_directory = os.environ["HOME"]
data_directory = os.path.join(home_directory, params.data_directory)
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


# create a symlink to the current data directory
if os.path.exists(current_symlink_path):
    os.remove(current_symlink_path)
    logger.info(f"Removed existing symlink {current_symlink_path}")
os.symlink(working_data_directory, current_symlink_path)
logger.info(f"Created symlink {current_symlink_path} -> {working_data_directory}")

# import modules that use the logger
import porter.sensors.sensors_handler as sh
import porter.threads as threads
import porter.valon as valon
from porter.telemetry.StatusBoard import StatusBoard

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

    flag = threading.Event()
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
        local_development = config.get("local_development", False)
        logger.info(f"Local development mode: {local_development}")

        sensors = config.get("sensors", None)
        source = config.get("source", None)
        camera = config.get("camera", None)
        status_writer_cfg = config.get("status_writer", None)

        # start the StatusWriter thread if configured
        # (telemd.py owns the XBee and reads the file written here)
        if status_writer_cfg is not None and status_writer_cfg.get("enabled", False):
            update_rate = status_writer_cfg.get("update_rate", 1.0)
            t = threads.StatusWriter(
                status_board=status_board,
                update_rate=update_rate,
                flag=flag,
                daemon=False,
            )
            t.start()
            owned_threads.append(t)
            logger.info(f"StatusWriter started at {update_rate} Hz")

        # start sensor threads if sensors are configured
        if sensors is not None:
            logger.info("Starting sensor threads...")
            sensor_names = {}
            sensor_handler = {}

            for i in sensors.keys():
                logger.info(f"Initializing sensor {i}")
                sensors_handler = sh.Handler(sensors[i], local=local_development)

                name = sensors[i]["name"]
                sensor_handler[name] = sensors_handler
                sensor_names[name] = name

            for i in sensor_handler.keys():
                logger.info(f"Starting thread for sensor {i}")
                t = threads.Sensors(
                    handler=sensor_handler[i],
                    flag=flag,
                    date=timestamp,
                    path=sensor_path,
                    sensor_name=sensor_names[i],
                    status_board=status_board,
                    daemon=False,
                )
                t.start()
                owned_threads.append(t)
                logger.info(f"Thread started for sensor {i}")

        # start Valon synthesizer if source is configured
        if source is not None:
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

            ATTEMPTS = 10
            valon_id = None
            for i in range(ATTEMPTS):
                logger.info(f"Attempt {i+1}/{ATTEMPTS} to get Valon ID...")
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
        if camera is not None and not local_development:
            try:
                if camera["name"] == 'Alvium_Starspec':
                    t = threads.AlviumCameraStarspec(
                        camera_config=camera,
                        flag=flag,
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
                        flag=flag,
                        path=camera_path,
                        status_board=status_board,
                        daemon=False,
                    )
                    t.start()
                    owned_threads.append(t)
                    logger.info(f"Thread started for camera {camera['name']}")
                elif camera["name"] == 'Sony':
                    t = threads.SonyCamera(
                        camera_config=camera,
                        flag=flag,
                        daemon=True,
                    )
                    t.start()
                    owned_threads.append(t)
                    logger.info(f"Thread started for camera {camera['name']}")
                else:
                    logger.error(f"Unknown camera name: {camera['name']}")
                    flag.set()

                time.sleep(2)

            except IndexError:
                flag.set()

        while not flag.is_set():
            time.sleep(0.2)

    except (ServiceExitError, FlagSetError) as err:
        logger.error(f"Exception occurred: {err.__class__.__name__}")
        flag.set()

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
