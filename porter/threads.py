import copy
import logging
import threading
import time

logger = logging.getLogger()


class SensorReading(threading.Thread):

    def __init__(
        self,
        handler,
        sensor_name,
        sensor_lock,
        reading_queue,
        main_flag,
        *args,
        **kwargs,
    ):

        super().__init__(*args, **kwargs)
        self.handler = handler
        self.sensor_name = sensor_name
        self.sensor_lock = sensor_lock
        self.reading_queue = reading_queue
        self.main_flag = main_flag

    def run(self):

        while not self.main_flag.is_set():
            self.handler.obj.read_data(self.reading_queue, self.sensor_lock)

        self.handler.obj.close()

        logger.info(f"Closed Connection to sensor {self.sensor_name}")


class SensorWriting(threading.Thread):

    def __init__(
        self,
        handler,
        sensor_lock,
        writing_queue,
        main_flag,
        *args,
        **kwargs,
    ):

        super().__init__(*args, **kwargs)
        self.handler = handler
        self.sensor_lock = sensor_lock
        self.writing_queue = writing_queue
        self.main_flag = main_flag

    def run(self):

        while not self.main_flag.is_set():
            self.handler.obj.write_data(self.writing_queue, self.sensor_lock)


class SensorSaving(threading.Thread):

    def __init__(
        self, handler, sensor_name, path, reading_queue, main_flag, date, *args, **kwargs
    ):

        super().__init__(*args, **kwargs)
        self.handler = handler
        self.reading_queue = reading_queue
        self.main_flag = main_flag

        name = path + sensor_name + "_" + date + ".bin"
        try:
            self.datafile = open(name, "r+b")
        except FileNotFoundError:
            self.datafile = open(name, "x+b")

    def run(self):
        
        with self.datafile as filename:
            while not self.main_flag.is_set():
                self.handler.obj.save_data(self.reading_queue, filename)


class Sensors(threading.Thread):

    def __init__(
        self,
        handler,
        sensor_lock,
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
            sensor_lock (threading.lock): lock to preserve multiple attempts to
                                          access the sensor queue
            flag (threading.Event): flag to communicate to the thread a
                                    particular event happened
            date (str): string with the date and time at the program start
            path (str): path for file storage
        """

        super().__init__(*args, **kwargs)

        self.sensor_lock = sensor_lock

        self.sensor_handler = handler

        self.sensor_name = sensor_name

        name = path + self.sensor_name + "_" + date + ".bin"
        try:
            self.datafile = open(name, "r+b")
        except FileNotFoundError:
            self.datafile = open(name, "x+b")

        self.shutdown_flag = flag

    def run(self):

        self.sensor_handler._connection()

        logging.info(f"Configuring {self.sensor_name}")

        self.sensor_handler._configuration()

        logging.info(f"Sensor {self.sensor_name} started")

        with self.datafile as binary:
            self.sensor_handler.obj.read_continous_binary(
                binary, self.shutdown_flag, self.sensor_lock
            )


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
                        logging.info(f"STOPPING")
                        break
                    else:
                        self.shutdown_flag.wait(video_chunks)
                        self.camera.messageHandler(["videocontrol"])
                        time.sleep(2)
                        secs_remaining -= video_chunks
                else:
                    flag = not flag

            self.camera.close_usb_connection()

        elif self.mode == "photo":
            photo_count = 0
            while not self.shutdown_flag.is_set():
                t = time.time()
                self.camera.messageHandler(["capture"])
                time.sleep(self.timing - (time.time() - t))

                photo_count += 1
                if photo_count > self.frames:
                    break

            self.camera.close_usb_connection()
