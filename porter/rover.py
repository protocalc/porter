import queue
import threading
import time
import pickle
import yaml
import telemetry.xbee as xbee
import random
import datetime
import os

import threads
import utils

import sensors.ublox as ubx
import sensors.KERNEL as KERNEL

import signal
import logging

import valon

try:
    import sensors.ads1115 as ads
except ModuleNotFoundError:
    pass

logging.basicConfig(
    filename='rover.log',
    filemode='w',
    format='%(asctime)s    %(levelname)s:%(message)s',
    datefmt='%m/%d/%Y %I:%M:%S',
    level=logging.DEBUG
    )


class mySerial:

    def __init__(self, port, baud, dev):

        self.port = port
        self.baud = baud
        self.dev = dev

    def read_msg(self, **kwargs):

        val = str(random.random())

        time.sleep(0.01)
        return val



class ubx_device(threading.Thread):

    def __init__(self, conn, tx_queue, qlock, ulock, flag, date, path, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.conn = conn
        self.tx_queue = tx_queue
        name = path+'/ubx_data'+date+'.pck'
        
        self.pck = open(name, 'ab')

        self.qlock = qlock
        self.ulock = ulock

        self.shutdown_flag = flag

    def run(self):

        while not self.shutdown_flag.is_set():
            self.ulock.acquire()
            msg = []
            msg.append('UBX')
            msg.append(self.conn.read_msg())
            self.ulock.release()
            if self.tx_queue is not None:
                self.qlock.acquire()
                self.tx_queue.put(msg)
                self.qlock.release()
            pickle.dump(msg, self.pck)

class adc_device(threading.Thread):

    def __init__(self, conn, tx_queue, qlock, alock, flag, date, path, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        self.conn = conn
        self.tx_queue = tx_queue
        
        name = path+'/adc_data'+date+'.pck'
        
        self.pck = open(name, 'ab')

        self.qlock = qlock
        self.alock = alock

        self.shutdown_flag = flag

    def run(self):

        while not self.shutdown_flag.is_set():
            self.alock.acquire()
            msg = []
            msg.append('ADC')
            msg.append(self.conn.get_voltage())
            print(msg)
            self.alock.release()
            if self.tx_queue is not None:
                self.qlock.acquire()
                self.tx_queue.put(msg)
                self.qlock.release()
            pickle.dump(msg, self.pck)

class inc_device(threading.Thread):

    def __init__(self, conn, tx_queue, qlock, ilock, flag, date, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.conn = conn
        self.tx_queue = tx_queue
        
        name = path+'/inc_data'+date+'.pck'
        
        self.pck = open(name, 'ab')

        self.qlock = qlock
        self.ilock = ilock

        self.shutdown_flag = flag

    def run(self):

        while not self.shutdown_flag.is_set():
            self.ilock.acquire()
            msg = []
            msg.append('INC')
            msg.append(self.conn.read_msg(return_binary=False))
            print(msg)
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
    
    path = os.path.dirname(os.path.realpath(__file__))

    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

    flag = threading.Event()

    cfg_path = path+'/config/rover_config.yml'

    with open(cfg_path, 'r') as cfg:
        config = yaml.safe_open(cfg)
    
    with utils.InterruptHandler as handler:
        if config['local_development']:
            pass
        
        else:
            synt=valon.valon(config['source']['port'], config['source']['baud'])

            synt.set_freq(config['source']['freq']/6)
            synt.set_pwr(config['source']['power'])
            if config['source']['mod_freq'] > 0:
                synt.set_amd(config['source']['mod_amp'],config['source']['mod_freq'])

            time.sleep(15)

            sensor_locks = {}
            sensor_names = {}
            sensor_connections = {}

            for i in config['sensors'].keys():
                
                if config['sensors'][i]['type'] == 'GPS':
                    
                    ubx_conn = ubx.UBX(
                        config['sensors'][i]['port'],
                        config['sensors'][i]['baudrate'], \
                        name = config['sensors'][i]['name']
                        )

                    conn = ubx_conn.conn

                    if 'configuration' in config['sensors'][i].keys():
                        ubx_config = ubx.UBXconfig(
                            serial_connection=conn,
                            name = config['sensors'][i]['name']
                            )
                        
                        ubx_config.configure(config['sensors'][i]['configuration'])
                
                elif config['sensors'][i]['type'] == 'Inclinometer':
                    
                    kernel_conn = KERNEL.KernelInertial(
                        config['sensors'][i]['port'],
                        config['sensors'][i]['baudrate'], \
                        name = config['sensors'][i]['name']
                        )

                    conn = kernel_conn.conn
                    
                    if 'configuration' in config['sensors'][i].keys():
                        conn.configure(config['sensors'][i]['configuration'])
                
                elif config['sensors'][i]['type'] == 'ADC':

                    conn = ads.ads1115(
                        config['sensors'][i]['channels'],
                        mode = config['sensors'][i]['mode'],
                        name = config['sensors'][i]['name'],
                        output_mode = config['sensors'][i]['output']
                    )

                    if 'configuration' in config['sensors'][i].keys():
                        conn.configure(config['sensors'][i]['configuration'])

                sensor_connections[config['sensors'][i]['name']] = conn
                sensor_locks[config['sensors'][i]['name']] = threading.Lock()
                sensor_names[config['sensors'][i]['name']] = config['sensors'][i]['name']

        date = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

        if not config['Telemetry']['in_use']:
            tx_queue = None
            tx_lock = None
        
        else:
            tx_queue = queue.Queue()
            tx_lock = threading.Lock()

            xbee_conn = xbee.comms(
                config['Telemetry']['antenna']['port'],
                config['Telemetry']['antenna']['baudrate'],
                config['Telemetry']['antenna']['remote']
                )
            xbee_lock = threading.Lock()
            

        for i in sensor_connections.keys():
            threads.Sensors(
                tx_queue = tx_queue,
                tx_lock = tx_lock,
                sensor_lock = sensor_locks[i],
                flag = flag,
                date = date,
                path = path,
                sensor_name = sensor_names[i]
            ).start()

        if tx_queue is not None:
            threads.Transmitter(xbee_conn, tx_queue, tx_lock, xbee_lock, flag, daemon=True).start()
            threads.Receiver(xbee_conn, sensor_connections, sensor_locks, xbee_lock, flag, daemon=True).start()

        
        if handler.interrupted:
            flag.set()

if __name__ == '__main__':
    main()
