import os
import copy
import logging
import threading
import time
import multiprocessing
import queue

try:
    from sour_core import sony
except ModuleNotFoundError:
    pass

logger = logging.getLogger("mainlogger")


class Sensors(threading.Thread):

    def __init__(
        self,
        handler,
        flag,
        date,
        path,
        sensor_name=None,
        *args,
        **kwargs,
    ):
        """Class to create a thread for each sensor

        Parameters:
            conn (Object): object with the connection to a specific sensor
            flag (threading.Event): flag to communicate to the thread a
                                    particular event happened
            date (str): string with the date and time at the program start
            path (str): path for file storage
        """

        super().__init__(*args, **kwargs)

        self.sensor_name = sensor_name

        self.datafile_name = path + self.sensor_name + "_" + date + ".bin"
        self.shutdown_flag = flag
        self.handler = handler

        # Initialize the sensor and start the sensor handler thread
        logger.info(f"Configuring {self.sensor_name}")
        self.handler._connection()
        self.handler._configuration()

    def run(self):
        # Block forever, getting data from the handler thread through the queue, until shutdown
        logger.info(f"Sensor {self.sensor_name} started")
        self.handler.obj.read_continous_binary(self.shutdown_flag, self.datafile_name)

        # Can only get here if shutdown flag is set
        logger.info(f"Sensor {self.sensor_name} closed")


class Camera(threading.Thread):

    def __init__(
        self,
        camera_config,
        flag,
        *args,
        **kwargs,
    ):
        """Class to create a thread for each sensor

        Parameters:
            camera (Object): camera object
            flag (threading.Event): flag to communicate to the thread a
                                    particular  event happened
            camera_mode (str): camera mode
            fps (float): number of fps in case of photo mode
            frames (int): number of photo in case of photo mode
            duration (float): duration of the video in case of video mode
        """

        super().__init__(*args, **kwargs)

        self.camera_config = camera_config

        self.camera_name = self.camera_config["name"]

        self.shutdown_flag = flag

    def run(self):

        camera = sony.SONYconn(self.camera_name)

        camera.initialize_camera()

        time.sleep(0.2)

        camera.messageHandler(["datetime", 0.04, 1e-3])

        time.sleep(0.1)

        camera.messageHandler(["programmode", self.camera_config["program"]])

        time.sleep(0.1)

        if "ISO" in self.camera_config.keys():
            camera.messageHandler(["iso", self.camera_config["ISO"]])
            time.sleep(0.1)

        if "shutter_speed" in self.camera_config.keys():
            camera.messageHandler(["shutterspeed", self.camera_config["shutter_speed"]])
            time.sleep(0.1)

        if "focus_distance" in self.camera_config.keys():
            camera.messageHandler(
                ["focusdistance", self.camera_config["focus_distance"]]
            )
            time.sleep(0.1)

        logger.info(f"Camera {self.camera_name} Configured")

        if self.camera_config["mode"] == "video":
            if "duration" in self.camera_config.keys():
                duration = self.camera_config["duration"]
            else:
                duration = 20 * 60

            flag = True
            video_chunks = 30 * 60
            secs_remaining = copy.copy(duration)
            while not self.shutdown_flag.is_set():
                time.sleep(0.1)
                camera.messageHandler(["videocontrol"])
                if flag:
                    if secs_remaining < video_chunks:
                        logger.info(
                            f"Camera {self.camera_name} starts recording, remaining {secs_remaining} s"
                        )
                        self.shutdown_flag.wait(secs_remaining)
                        camera.messageHandler(["videocontrol"])
                        self.shutdown_flag.set()
                        flag = not flag
                        logger.info(f"Camera {self.camera_name} stops recording")
                        break
                    else:
                        self.shutdown_flag.wait(video_chunks)
                        camera.messageHandler(["videocontrol"])
                        time.sleep(2)
                        secs_remaining -= video_chunks
                else:
                    flag = not flag
                    
            print('CAMERA OUT')

        elif self.camera_config["mode"] == "photo":
            if "fps" in self.camera_config.keys():
                fps = self.camera_config["fps"]
            else:
                fps = 1

            if "frames" in self.camera_config.keys():
                frames = self.camera_config["frames"]
            else:
                frames = 1e9

            timing = 1 / fps

            photo_count = 0
            while not self.shutdown_flag.is_set():
                t = time.time()
                camera.messageHandler(["capture"])

                while (time.time() - t) < timing:
                    pass

                photo_count += 1
                if photo_count > frames:
                    break

        logger.info(f"Camera {self.camera_name} stopped")

        camera.close_usb_connection()
