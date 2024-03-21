import queue
import threading
import time
import yaml
import porter.telemetry.xbee as xbee
import datetime
import os
import signal
import sys

import porter.threads as threads

import porter.sensors.sensors_handler as sh

try:
    import sour_core.sony.SONYconn as cam
except ModuleNotFoundError:
    pass
import logging

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
    format="%(asctime)s  [%(threadName)s]  %(levelname)s:%(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
    level=logging.DEBUG,
)

logger = logging.getLogger("mainlogger")

"""
Classes and Function to deal with interrupting the code
"""


class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """

    pass


def handler(signum, frame):
    logger.info(f"Caught signal {signal.strsignal(signum)}")
    raise ServiceExit


signal_to_catch = [
    signal.SIGINT,
    signal.SIGTERM,
]


def main():

    cfg_name = sys.argv[1]

    flag = threading.Event()

    cfg_path = path + "/" + cfg_name

    with open(cfg_path, "r") as cfg:
        config = yaml.safe_load(cfg)

    if not os.path.exists(home_dir + "/data/" + date + "/sensors_data"):
        os.mkdir(home_dir + "/data/" + date + "/sensors_data")
        sensor_path = home_dir + "/data/" + date + "/sensors_data/"

    for sig in signal_to_catch:
        signal.signal(sig, handler)

    tx_queue = None
    tx_lock = None

    try:

        if "sensors" in config.keys():

            sensor_locks = {}
            sensor_names = {}
            sensor_connections = {}

            for i in config["sensors"].keys():

                sensors_handler = sh.Handler(
                    config["sensors"][i], local=config["local_development"]
                )

                name = config["sensors"][i]["name"]

                sensor_connections[name] = sensors_handler.obj
                sensor_locks[name] = threading.Lock()
                sensor_names[name] = name

            if not config["telemetry"]["enabled"]:
                tx_queue = None
                tx_lock = None

            else:
                tx_queue = queue.Queue()
                tx_lock = threading.Lock()

                xbee_conn = xbee.comms(
                    config["Telemetry"]["antenna"]["port"],
                    config["Telemetry"]["antenna"]["baudrate"],
                    config["Telemetry"]["antenna"]["remote"],
                )
                xbee_lock = threading.Lock()

            for i in sensor_connections.keys():
                threads.Sensors(
                    conn=sensor_connections[i],
                    tx_queue=tx_queue,
                    tx_lock=tx_lock,
                    sensor_lock=sensor_locks[i],
                    flag=flag,
                    date=date,
                    path=sensor_path,
                    sensor_name=sensor_names[i],
                    daemon=True,
                ).start()

        if "source" in config.keys():

            synt = valon.valon(config["source"]["port"], config["source"]["baudrate"])

            synt.set_freq(config["source"]["freq"] / 6)
            synt.set_pwr(config["source"]["power"])
            if config["source"]["mod_freq"] > 0:
                synt.set_amd(config["source"]["mod_amp"], config["source"]["mod_freq"])

            time.sleep(2)

        if "camera" in config.keys() and not config["local_development"]:

            camera = cam(config["camera"]["name"])

            camera.initialize_camera()

            camera.messageHandler(["datetime"])

            camera.messageHandler(["programmode", config["camera"]["program"]])

            if "iso" in config["camera"].keys():
                camera.messageHandler(["iso", config["camera"]["iso"]])

            if "shutter_speed" in config["camera"].keys():
                camera.messageHandler(
                    ["shutterspeed", config["camera"]["shutter_speed"]]
                )

            if "focus_distance" in config["camera"].keys():
                camera.messageHandler(
                    ["focus_distance", config["camera"]["focus_distance"]]
                )

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

        if tx_queue is not None:
            threads.Transmitter(
                xbee_conn, tx_queue, tx_lock, xbee_lock, flag, daemon=True
            ).start()
            threads.Receiver(
                xbee_conn,
                sensor_connections,
                sensor_locks,
                xbee_lock,
                flag,
                daemon=True,
            ).start()

        while True:
            pass

    except ServiceExit:
        flag.set()

        for i in sensor_connections.keys():
            sensor_connections[i].close()
            logging.info(f"Sensor {sensor_names[i]} closed")

        if "camera" in config.keys() and not config["local_development"]:
            if camera._recording_status():
                camera.video_control()


if __name__ == "__main__":
    main()
