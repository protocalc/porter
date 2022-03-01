import queue
import threading
import time
import pickle
import configparser
import ublox.ublox as ublox
import telemetry.xbee as xbee
import random

import subprocess
import shlex
import signal

import inclinometer as inc

try:
    import ads1115 as ads
except ModuleNotFoundError:
    pass

class mySerial:

    def __init__(self, port, baud, dev):

        self.port = port
        self.baud = baud
        self.dev = dev

    def read_msg(self, **kwargs):

        val = str(random.random())

        time.sleep(0.01)
        return val

class receiver(threading.Thread):

    def __init__(self, xbee_obj, conn_dict, xlock, flag, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.xbee_obj = xbee_obj
        self.conn_dict = conn_dict

        self.xlock = xlock

        self.shutdown_flag = flag

    def run(self):

        while not self.shutdown_flag.is_set():

            self.xlock.acquire()
            dest, msg = self.xbee_obj.poll_msg()
            self.xlock.release()

            if dest == 'UBX':
                self.conn_dict['UBX'][1].acquire()
                self.conn_dict['UBX'][0].conn.write(msg)
                self.conn_dict['UBX'][1].release()
            elif dest == 'ADC':
                self.conn_dict['ADC'][1].acquire()
                self.conn_dict['ADC'][0].set_gain(float(msg.decode()))
                self.conn_dict['ADC'][1].release()

class transmitter(threading.Thread):

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

class ubx_device(threading.Thread):

    def __init__(self, conn, tx_queue, qlock, ulock, flag, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.conn = conn
        self.tx_queue = tx_queue
        self.pck = open('ubx_data.pck', 'ab')

        self.qlock = qlock
        self.ulock = ulock

        self.shutdown_flag = flag

    def run(self):

        while not self.shutdown_flag.is_set():
            print('UBX', self.shutdown_flag.is_set())
            self.ulock.acquire()
            msg = []
            msg.append('UBX')
            msg.append(time.time())
            msg.append(self.conn.read_msg())
            self.ulock.release()
            if self.tx_queue is not None:
                self.qlock.acquire()
                self.tx_queue.put(msg)
                self.qlock.release()
            pickle.dump(msg, self.pck)

class adc_device(threading.Thread):

    def __init__(self, conn, tx_queue, qlock, alock, flag, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        self.conn = conn
        self.tx_queue = tx_queue
        self.pck = open('adc_data.pck', 'ab')

        self.qlock = qlock
        self.alock = alock

        self.shutdown_flag = flag

    def run(self):

        while not self.shutdown_flag.is_set():
            self.alock.acquire()
            msg = []
            msg.append('ADC')
            msg.append(time.time())
            msg.append(self.conn.get_voltage())
            self.alock.release()
            if self.tx_queue is not None:
                self.qlock.acquire()
                self.tx_queue.put(msg)
                self.qlock.release()
            pickle.dump(msg, self.pck)

class inc_device(threading.Thread):

    def __init__(self, conn, tx_queue, qlock, ilock, flag, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.conn = conn
        self.tx_queue = tx_queue
        self.pck = open('inc_data.pck', 'ab')

        self.qlock = qlock
        self.ilock = ilock

        self.shutdown_flag = flag

    def run(self):

        while not self.shutdown_flag.is_set():
            print('INC', self.shutdown_flag.is_set())
            self.ilock.acquire()
            msg = []
            msg.append('INC')
            msg.append(time.time())
            msg.append(self.conn.read_msg(return_binary=True))
            self.ilock.release()
            if self.tx_queue is not None:
                self.qlock.acquire()
                self.tx_queue.put(msg)
                self.qlock.release()
            pickle.dump(msg, self.pck)

'''
Classes and Function to deal with interrupting the code 
'''

class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass

def service_shutdown(signum, frame):
    print('Caught signal %d' % signum)
    raise ServiceExit


def main():

    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

    flag = threading.Event()

    cfg = configparser.ConfigParser()
    cfg.read('config/rover_config.cfg')

    ubx_port = cfg.get('UBX', 'port')
    ubx_baud = cfg.get('UBX', 'baud')

    xbee_port = cfg.get('XBEE', 'port')
    xbee_baud = cfg.get('XBEE', 'baud')
    xbee_remote = cfg.get('XBEE', 'remote')
    xbee_use = cfg.get('XBEE', 'use')

    inc_port = cfg.get('INC', 'port')
    inc_baud = cfg.get('INC', 'baud')
    inc_address = cfg.get('INC', 'address')

    local = cfg.get('LOCAL', 'local_dev')

    try:
        # cmd = 'gphoto2 --wait-event=4s --interval=1 --frames=100 --capture-image-and-download --filename=%Y%m%d-%H%M%S-%03n.%C'
        # cmds = shlex.split(cmd)

        # p = subprocess.Popen(cmds, close_fds=True)

        if local == 'True':

            ubx_conn = mySerial(ubx_port, ubx_baud, dev='UBX')
            inc_conn = mySerial(inc_port, inc_baud, dev='INC')
            adc_conn = None #Due to the ads library for local development no ADC connection is created
        else:
            ubx_conn = ublox.UBXio(ubx_port, ubx_baud)
            inc_conn = inc.inclinometer(inc_port, inc_address, inc_baud)
            adc_conn = ads.ads1115([0,1], mode='differential')

        qlock = threading.Lock()
        ulock = threading.Lock()
        alock = threading.Lock()
        ilock = threading.Lock()
        xlock = threading.Lock()

        sensors = {
            'UBX': [ubx_conn, ulock],
            'ADC': [adc_conn, alock],
            'INC': [inc_conn, ilock]
        }
        
        if xbee_use == 'True':
            xbee_conn = xbee.comms(xbee_port, xbee_baud, xbee_remote)
            tx_queue = queue.Queue()
        else:
            tx_queue = None

        ubx_device(ubx_conn, tx_queue, qlock, ulock, flag, daemon=True).start()
        inc_device(inc_conn, tx_queue, qlock, ilock, flag, daemon=True).start()

        if tx_queue is not None:
            adc_device(adc_conn, tx_queue, qlock, alock, daemon=True).start()
            transmitter(xbee_conn, tx_queue, qlock, xlock, daemon=True).start()
            receiver(xbee_conn, sensors, xlock, daemon=True).start()

        while True:
            pass

    except ServiceExit:
        # Terminate the running threads.
        # Set the shutdown flag on each thread to trigger a clean shutdown of each thread.
        flag.set()

if __name__ == '__main__':
    main()






