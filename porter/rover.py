import queue
import threading
import time
import pickle
import configparser
import ublox.ublox as ublox
import telemetry.xbee as xbee

import ads1115 as ads
import inclinometer as inc


class receiver(threading.Thread):

    def __init__(self, xbee_obj, conn_dict, xlock, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.xbee_obj = xbee_obj
        self.conn_dict = conn_dict

        self.xlock = xlock

    def run(self):

        while True:

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

    def __init__(self, xbee_obj, tx_queue, qlock, xlock, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.xbee_obj = xbee_obj
        self.tx_queue = tx_queue
        
        self.qlock = qlock
        self.xlock = xlock

    def run(self):

        while True:
            while not self.tx_queue.empty():
                self.qlock.acquire()
                self.xlock.acquire()
                self.xbee_obj.send_msg(self.tx_queue.get())
                self.qlock.release()
                self.xlock.release()

class ubx_device(threading.Thread):

    def __init__(self, conn, tx_queue, qlock, ulock, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.conn = conn
        self.tx_queue = tx_queue
        self.pck = open('ubx_log.pck', 'ab')

        self.qlock = qlock
        self.ulock = ulock 

    def run(self):

        while True:

            self.ulock.acquire()
            msg = 'UBX'
            msg += self.conn.read_msg()
            self.ulock.release()
            self.qlock.acquire()
            self.tx_queue.put(msg)
            self.qlock.release()
            pickle.dump(msg, self.pck)

class adc_device(threading.Thread):

    def __init__(self, conn, tx_queue, qlock, alock, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.conn = conn
        self.tx_queue = tx_queue
        self.pck = open('adc_log.pck', 'ab')

        self.qlock = qlock
        self.alock = alock

    def run(self):

        while True:
            self.alock.acquire()
            msg = 'ADC'
            msg += self.conn.get_voltage()
            self.alock.release()
            self.qlock.acquire()
            self.tx_queue.put(msg)
            self.qlock.release()
            pickle.dump(msg, self.pck)

class inc_device(threading.Thread):

    def __init__(self, conn, tx_queue, qlock, ilock, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.conn = conn
        self.tx_queue = tx_queue
        self.pck = open('inc_log.pck', 'ab')

        self.qlock = qlock
        self.ilock = ilock

    def run(self):

        while True:
            self.ilock.acquire()
            msg = 'INC'
            msg += self.conn.get_xy_angles(return_binary=True)
            self.ilock.release()
            self.qlock.acquire()
            self.tx_queue.put(msg)
            self.qlock.release()
            pickle.dump(msg, self.pck)


def main():
    
    cfg = configparser.ConfigParser()
    cfg.read('rover_config.cfg')

    ubx_port = cfg.get('UBX', 'port')
    ubx_baud = cfg.get('UBX', 'baud')

    xbee_port = cfg.get('XBEE', 'port')
    xbee_baud = cfg.get('XBEE', 'baud')
    xbee_remote = cfg.get('XBEE', 'remote')

    inc_port = cfg.get('INC', 'port')
    inc_baud = cfg.get('INC', 'baud')
    inc_address = cfg.get('INC', 'address')
    
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

    xbee_conn = xbee.comms(xbee_port, xbee_baud, xbee_remote)

    tx_queue = queue.Queue()

    ubx_device(ubx_conn, tx_queue, qlock, ulock, daemon=True).start()
    adc_device(adc_conn, tx_queue, qlock, alock, daemon=True).start()
    inc_device(inc_conn, tx_queue, qlock, ilock, daemon=True).start()
    transmitter(xbee_conn, tx_queue, qlock, xlock, daemon=True).start()
    receiver(xbee_conn, sensors, xlock, daemon=True).start()

    try:
        while True:
            time.sleep(3)
    except KeyboardInterrupt:
        print("Exiting")

if __name__ == '__main__':
    main()






