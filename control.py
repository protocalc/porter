import datetime
import logging
import os
import queue
import signal
import sys
import threading
import time

import subprocess

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
logger.setLevel(logging.DEBUG)

logfile = logging.FileHandler(home_dir + "/data/" + date + "/file.log")
logfile.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s.%(msecs)03d  [%(threadName)s]  %(levelname)s:%(message)s",
    datefmt="%Y/%m/%d %H:%M:%S"
    )
logfile.setFormatter(formatter)

logger.addHandler(logfile)

log_path = home_dir + "/data/" + date + "/file.log"

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
    
    print(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

    flag = threading.Event()

    cfg_path = path + "/" + cfg_name
    
    cfg_path_copy = home_dir + "/data/" + date + "/" + cfg_name.split("/")[-1]

    status = True

    with open(cfg_path, "r") as cfg:
        config = yaml.safe_load(cfg)
        logger.info(f"Loaded configuration {cfg_name}")
    
    os.popen(f"cp {cfg_path} {cfg_path_copy}")
    
    if not os.path.exists(home_dir + "/data/" + date + "/sensors_data"):
        os.mkdir(home_dir + "/data/" + date + "/sensors_data")
        sensor_path = home_dir + "/data/" + date + "/sensors_data/"

    for sig in signal_to_catch:
        signal.signal(sig, handler)
        
    counter = 0
    
    # while True:
        # try:
            # result = subprocess.run(["gpsctl"], check=True, capture_output=True, text=True)
            # logger.info(f"Current GPS devices connected to GPSD: {result.stdout}")
            # break
        # except:
            # logger.info(f"Trying to recconect to GPSD")
            # time.sleep(0.1)
            # counter += 1
            # if counter > 100:
                # break


    time.sleep(1)

    try:
        if "sensors" in config.keys():
            sensor_names = {}
            sensor_handler = {}

            for i in config["sensors"].keys():
                sensors_handler = sh.Handler(
                    config["sensors"][i], local=config["local_development"]
                )

                name = config["sensors"][i]["name"]

                sensor_handler[name] = sensors_handler
                sensor_names[name] = name

            for i in sensor_handler.keys():
                threads.Sensors(
                    handler=sensor_handler[i],
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

            for i in range(10):
                valon_id = synt.get_id()
                time.sleep(0.01)
            
            time.sleep(2)

        if "camera" in config.keys() and not config["local_development"]:

            try:
                threads.Camera(
                    camera_config=config["camera"],
                    flag=flag,
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

        while not flag.is_set():
            time.sleep(0.1)
        
        capture_flag(flag)

    except (ServiceExitError, FlagSetError) as err:
        logger.info(f"Flag has been raise")
        flag.set()


if __name__ == "__main__":
    main()
