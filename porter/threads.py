import os
import copy
import logging
import threading
import time
import multiprocessing

from multiprocessing import Process, SimpleQueue, freeze_support

logger = logging.getLogger()

def CoreThread(handler, signal_queue, data_queue, affinity_mask=None):
    # Set core
    if affinity_mask is not None:
        os.sched_setaffinity(0, affinity_mask)`

    # Configure
    handler._connection()
    handler._configuration()

    # Read continuously; blocks until signaled to stop
    handler.obj.read_continous_binary(signal_queue, data_queue)

class Sensors(threading.Thread):

    def __init__(
        self,
        handler,
        flag,
        date,
        path,
        sensor_name=None,
        affinity_mask=None,
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

        name = path + self.sensor_name + "_" + date + ".bin"
        try:
            self.datafile = open(name, "r+b")
        except FileNotFoundError:
            self.datafile = open(name, "x+b")

        self.shutdown_flag = flag

        # Spawn mpsc queues
        self.signal_queue = SimpleQueue()
        self.data_queue = SimpleQueue()

        # Initialize the sensor and start the sensor handler thread
        logging.info(f'Configuring {self.sensor_name}')
        logging.info(f"Sensor {self.sensor_name} started")

        p = Process(target=CoreThread, args=(handler, self.signal_queue, self.data_queue, affinity_mask))
        p.start()

    def run(self):
        # Loop forever, getting data from the handler thread through the queue, until shutdown
        while not self.shutdown_flag.is_set():
            try:
                # Get the data
                data = self.data_queue.get(False)

                # Write the data to disk
                self.datafile.write(data)
            except SimpleQueue.Empty:
                # No data, so sleep
                time.sleep(1)
            except Exception:
                # Something is wrong with the queue, so assume closed
                logging.error(f"Sensor {self.sensor_name} data queue closed")
                break

        # Send signal to sensor thread to shutdown
        self.signal_queue.put(None, False)

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
        affinity_mask=None,
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

        if affinity_mask is not None:
            os.sched_setaffinity(0, affinity_mask)

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
