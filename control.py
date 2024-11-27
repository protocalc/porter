import datetime
import logging
import os
import queue
import signal
import sys
import threading
import time

import yaml

import porter.sensors.sensors_handler as sh
import porter.threads as threads
import porter.valon as valon

path = os.path.dirname(os.path.realpath(__file__))
home_dir = os.environ["HOME"]

date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

if not os.path.exists(home_dir + "/data"):
    os.mkdir(home_dir + "/data")
if not os.path.exists(path + "/data/" + date):
    os.mkdir(home_dir + "/data/" + date)

logging.basicConfig(
    filename=home_dir + "/data/" + date + "/file.log",
    filemode="w",
    format="%(asctime)s.%(msecs)03d  [%(threadName)s]  %(levelname)s:%(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
    level=logging.DEBUG,
)

logger = logging.getLogger("mainlogger")

try:
    from sour_core import sony
except ModuleNotFoundError:
    pass

"""
Classes and Function to deal with interrupting the code
"""


class ServiceExitError(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """

    pass


class FlagSetError(Exception):

    pass


def handler(signum, frame):
    print("Signal Sent")
    logger.info(f"Caught signal {signal.strsignal(signum)}")
    raise ServiceExitError


def capture_flag(flag):
    logger.info(f"Flag has been set in a Thread")
    if flag.is_set():
        raise FlagSetError


signal_to_catch = [
    signal.SIGINT,
    signal.SIGTERM,
]


def main():
    cfg_name = sys.argv[1]

    flag = threading.Event()

    cfg_path = path + "/" + cfg_name

    status = True

    with open(cfg_path, "r") as cfg:
        config = yaml.safe_load(cfg)
        logging.info(f"Loaded configuration {cfg_name}")

    if not os.path.exists(home_dir + "/data/" + date + "/sensors_data"):
        os.mkdir(home_dir + "/data/" + date + "/sensors_data")
        sensor_path = home_dir + "/data/" + date + "/sensors_data/"

    for sig in signal_to_catch:
        signal.signal(sig, handler)

    time.sleep(2)

    try:
        if "sensors" in config.keys():
            sensor_locks = {}
            sensor_names = {}
            sensor_handler = {}

            for i in config["sensors"].keys():
                logging.info(f'Sensor {i}')
                sensors_handler = sh.Handler(
                    config["sensors"][i], local=config["local_development"]
                )

                name = config["sensors"][i]["name"]
                
                sensor_handler[name] = sensors_handler
                sensor_locks[name] = threading.Lock()
                sensor_names[name] = name

            for i in sensor_handler.keys():
                logging.info(f'Sensor {i} - {sensor_handler[i]}')
                threads.Sensors(
                    handler=sensor_handler[i],
                    sensor_lock=sensor_locks[i],
                    flag=flag,
                    date=date,
                    path=sensor_path,
                    sensor_name=sensor_names[i],
                    daemon=False,
                ).start()

        if "source" in config.keys():
            synt = valon.Valon(config["source"]["port"], config["source"]["baudrate"])

            synt.set_freq(config["source"]["freq"] / config["source"]["mult_factor"])
            synt.set_pwr(config["source"]["power"])
            if config["source"]["mod_freq"] > 0:
                synt.set_amd(config["source"]["mod_amp"], config["source"]["mod_freq"])
            else:
                synt.set_amd(0, 0)
            time.sleep(2)

        if "camera" in config.keys() and not config["local_development"]:

            try:
                camera = sony.SONYconn(config["camera"]["name"])

                camera.initialize_camera()

                time.sleep(0.2)

                camera.messageHandler(["datetime", 0.04, 1e-3])

                time.sleep(0.1)

                camera.messageHandler(["programmode", config["camera"]["program"]])

                time.sleep(0.1)

                if "ISO" in config["camera"].keys():
                    camera.messageHandler(["iso", config["camera"]["ISO"]])
                    time.sleep(0.1)

                if "shutter_speed" in config["camera"].keys():
                    camera.messageHandler(
                        ["shutterspeed", config["camera"]["shutter_speed"]]
                    )
                    time.sleep(0.1)

                if "focus_distance" in config["camera"].keys():
                    camera.messageHandler(
                        ["focusdistance", config["camera"]["focus_distance"]]
                    )
                    time.sleep(0.1)

                if config["camera"]["mode"] == "photo":
                    duration = None

                    if "fps" in config["camera"].keys():
                        fps = config["camera"]["fps"]
                    else:
                        fps = 1

                    if "frames" in config["camera"].keys():
                        frames = config["camera"]["frames"]
                    else:
                        frames = None

                else:
                    if "duration" in config["camera"].keys():
                        duration = config["camera"]["duration"]
                    else:
                        duration = None

                    fps = None
                    frames = None

                threads.Camera(
                    camera=camera,
                    flag=flag,
                    mode=config["camera"]["mode"],
                    camera_name=config["camera"]["name"],
                    fps=fps,
                    frames=frames,
                    duration=duration,
                    daemon=True,
                ).start()

                time.sleep(2)

            except IndexError:
                status = False
                flag.set()
                logger.info("Camera not Found, deleting data folder")
                logger.info("This command is sent so that when the code")
                logger.info("run at startup, we do not fill the data directory")

                original_log_name = home_dir + "/data/" + date + "/file.log"

                new_log_name = home_dir + "/data/file_" + date + ".log"
                time.sleep(1)
                os.popen(f"cp {original_log_name} {new_log_name}")
                time.sleep(2)

                import shutil

                shutil.rmtree(home_dir + "/data/" + date)

        while status:
            pass

        capture_flag(flag)

    except (ServiceExitError, FlagSetError) as err:
        logger.info(f"Flag has been raise")
        if flag.is_set():
            logger.info(f"CASE 1")
            if "camera" in config.keys() and not config["local_development"]:
                try:
                    camera.close_usb_connection()
                except UnboundLocalError:
                    pass
        else:
            flag.set()
            logger.info(f"CASE 2")
            if "camera" in config.keys() and not config["local_development"]:
                camera.close_usb_connection()


if __name__ == "__main__":
    main()
