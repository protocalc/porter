import threading
import pickle
import logging
#import signal

logger = logging.getLogger()

class Sensors(threading.Thread):

    def __init__(self, conn, tx_queue, tx_lock, sensor_lock, flag, date, path, \
                 sensor_name=None, chunk_size=250, *args, **kwargs):

        """Class to create a thread for each sensor

        Parameters:
            conn (Object): object with the connection to a specific sensor
            tx_queue (Queue.queue): queue to add the readings to a transmitting queue common to all sensors
            tx_lock (threading.lock): lock to preserve multiple attempts to access the transmitting queue
            sensor_lock (threading.lock): lock to preserve multiple attempts to access the sensor queue
            flag (threading.Event): flag to communicate to the thread a particular event happened
            date (str): string with the date and time at the program start
            path (str): path for file storage
        """

        super().__init__(*args, **kwargs)

        self.conn = conn
        self.tx_queue = tx_queue

        self.tx_lock = tx_lock
        self.sensor_lock = sensor_lock

        self.sensor_name = sensor_name
        self.chunk_size = chunk_size

        name = path+'/sensors_data/'+self.sensor_name+'_'+date+'.pck'
        self.pck = open(name, 'ab')

        self.shutdown_flag = flag

    def run(self):

        logging.info(f'Sensor {self.sensor_name} started')

        while not self.shutdown_flag.is_set():
            self.sensor_lock.acquire()
            temp = self.conn.read(self.chunk_size)
            self.sensor_lock.release()
            if self.tx_queue is not None:
                self.tx_lock.acquire()
                msg = []
                msg.append(self.sensor_name)
                msg.append(temp)
                self.tx_queue.put(msg)
                self.tx_lock.release()
            pickle.dump(temp, self.pck)


class Receiver(threading.Thread):

    def __init__(self, xbee_obj, destination_connections, destination_locks, xlock, flag, *args, **kwargs):

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
