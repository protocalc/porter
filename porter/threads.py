import threading
import logging
import time
import copy

logger = logging.getLogger()

class Sensors(threading.Thread):

    def __init__(
        self,
        conn,
        tx_queue,
        tx_lock,
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
            tx_queue (Queue.queue): queue to add the readings to a transmitting
                                    queue common to all sensors
            tx_lock (threading.lock): lock to preserve multiple attempts to
                                      access the transmitting queue
            sensor_lock (threading.lock): lock to preserve multiple attempts to
                                          access the sensor queue
            flag (threading.Event): flag to communicate to the thread a
                                    particular event happened
            date (str): string with the date and time at the program start
            path (str): path for file storage
        """

        super().__init__(*args, **kwargs)

        self.conn = conn
        self.tx_queue = tx_queue

        self.tx_lock = tx_lock
        self.sensor_lock = sensor_lock

        self.sensor_name = sensor_name

        name = path + self.sensor_name + "_" + date + ".bin"
        try:
            self.datafile = open(name, "r+b")
        except FileNotFoundError:
            self.datafile = open(name, "x+b")

        self.shutdown_flag = flag

    def run(self):

        logging.info(f"Sensor {self.sensor_name} started")

        with self.datafile as binary:
            while not self.shutdown_flag.is_set():
                self.sensor_lock.acquire()
                temp = self.conn.read()
                self.sensor_lock.release()
                if self.tx_queue is not None:
                    self.tx_lock.acquire()
                    msg = []
                    msg.append(self.sensor_name)
                    msg.append(temp)
                    self.tx_queue.put(msg)
                    self.tx_lock.release()
                binary.write(temp)
                binary.flush()
            print('Sensor Closing')                
            self.conn.close()


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
            self.duration = 1e9

        self.shutdown_flag = flag

    def run(self):

        logging.info(f"Camera {self.camera_name} started")

        if self.mode == "video":
            flag = True
            video_chunks = 20 * 60 
            secs_remaining = copy.copy(self.duration)
            while not self.shutdown_flag.is_set():
                time.sleep(0.1)
                self.camera.messageHandler(["videocontrol"])
                if flag:
                    if secs_remaining < video_chunks:
                        self.shutdown_flag.wait(secs_remaining)
                        self.camera.messageHandler(["videocontrol"])
                        self.shutdown_flag.set()
                        flag = not flag
                        break
                    else: 
                        self.shutdown_flag.wait(video_chunks)
                        self.camera.messageHandler(["videocontrol"])
                        time.sleep(2)
                        secs_remaining -= video_chunks
                else:
                    flag = not flag
            self.camera.messageHandler(["videocontrol"])

        elif self.mode == "photo":
            photo_count = 0
            while not self.shutdown_flag.is_set():
                t = time.time()
                self.camera.messageHandler(["capture"])
                time.sleep(self.timing - (time.time() - t))

                photo_count += 1
                if photo_count > self.frames:
                    break


class Receiver(threading.Thread):

    def __init__(
        self,
        xbee_obj,
        destination_connections,
        destination_locks,
        xlock,
        flag,
        *args,
        **kwargs,
    ):

        super().__init__(*args, **kwargs)

        self.xbee_obj = xbee_obj
        self.destination_connections = destination_connections
        self.destination_locks = destination_locks

        self.xlock = xlock

        self.shutdown_flag = flag

    def run(self):

        while not self.shutdown_flag.is_set():

            self.xlock.acquire()
            dest, msg = self.xbee_obj.poll_msg()
            self.xlock.release()

            self.destination_locks[dest].acquire()
            self.destination_connections.write(msg)
            self.destination_locks[dest].release()


class Transmitter(threading.Thread):

    def __init__(self, xbee_obj, tx_queue, qlock, xlock, flag, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.xbee_obj = xbee_obj
        self.tx_queue = tx_queue

        self.qlock = qlock
        self.xlock = xlock

        self.shutdown_flag = flag

    def run(self):

        while not self.shutdown_flag.is_set():
            while not self.tx_queue.empty():
                self.qlock.acquire()
                self.xlock.acquire()
                self.xbee_obj.send_msg(self.tx_queue.get())
                self.qlock.release()
                self.xlock.release()
