import os
import copy
import logging
import threading
import time
import multiprocessing
import queue

logger = logging.getLogger()

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
        logging.info(f'Configuring {self.sensor_name}')
        self.handler._connection()
        self.handler._configuration()

    def run(self):
        # Block forever, getting data from the handler thread through the queue, until shutdown
        logging.info(f"Sensor {self.sensor_name} started")
        self.handler.obj.read_continous_binary(self.shutdown_flag, self.datafile_name)

        # Can only get here if shutdown flag is set
        logging.info(f"Sensor {self.sensor_name} closed")

class Camera(threading.Thread):

    def __init__(
        self,
        camera,
        flag,
        mode,
        camera_name=None,
        fps=2,
        frames=None,
        duration=None,
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

        self.camera = camera

        self.camera_name = camera_name
        self.mode = mode

        if fps is not None:
            self.timing = 1 / fps
        else:
            self.timing = None

        if frames is not None:
            self.frames = int(frames)
        else:
            self.frames = int(1e9)

        if duration is not None:
            self.duration = duration
        else:
            self.duration = 20 * 60

        self.shutdown_flag = flag

    def run(self):

        logging.info(f"Camera {self.camera_name} started")

        if self.mode == "video":
            flag = True
            video_chunks = 30 * 60
            secs_remaining = copy.copy(self.duration)
            while not self.shutdown_flag.is_set():
                time.sleep(0.1)
                self.camera.messageHandler(["videocontrol"])
                if flag:
                    if secs_remaining < video_chunks:
                        logging.info(f"RECORDING {secs_remaining}")
                        self.shutdown_flag.wait(secs_remaining)
                        self.camera.messageHandler(["videocontrol"])
                        self.shutdown_flag.set()
                        flag = not flag
                        logging.info("STOPPING")
                        break
                    else:
                        self.shutdown_flag.wait(video_chunks)
                        self.camera.messageHandler(["videocontrol"])
                        time.sleep(2)
                        secs_remaining -= video_chunks
                else:
                    flag = not flag

        elif self.mode == "photo":
            photo_count = 0
            while not self.shutdown_flag.is_set():
                t = time.time()
                self.camera.messageHandler(["capture"])
                time.sleep(self.timing - (time.time() - t))

                photo_count += 1
                if photo_count > self.frames:
                    break
