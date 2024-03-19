import threading
import time
import yaml
import datetime
import os
import signal

import threads as threads

import sensors.sensors_handler as sh

import camera.PTPUsb as cam
import logging

path = os.path.dirname(os.path.realpath(__file__))
date = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

logname = path+'/calib_'+date+'.log'

logging.basicConfig(
    filename=logname,
    filemode='w',
    format='%(asctime)s    [%(threadName)s]    %(levelname)s:%(message)s',
    datefmt='%m/%d/%Y %H:%M:%S',
    level=logging.DEBUG
    )

logger = logging.getLogger('mainlogger')

'''
Classes and Function to deal with interrupting the code
'''

class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass

def handler(signum, frame):
    logger.info(f'Caught signal {signal.strsignal(signum)}')
    raise ServiceExit

signal_to_catch = [
    signal.SIGINT,
    signal.SIGTERM,
]


def main():

    flag = threading.Event()
    #flag = None

    cfg_path = path+'/config/calib_config.yml'

    with open(cfg_path, 'r') as cfg:
        config = yaml.safe_load(cfg)

    if not os.path.exists(path+'/sensors_data'):
        os.mkdir(path+'/sensors_data')

    for sig in signal_to_catch:
        signal.signal(sig, handler)

    try:

        if 'camera' in config.keys():

            camera = cam.PTPusb(path, date, config['camera']['name'])
            camera.initialize_camera()

            camera.set_datetime()

            if config['camera']['mode'] == 'photo':
                mode = config['camera']['program']
                if 'fps' in config['camera'].keys():
                    fps = config['camera']['fps']
                else:
                    fps = 2
            elif config['camera']['mode'] == 'video':
                mode = 'MovieM'
                fps = None

            camera.set_camera_mode(mode=mode)

            threads.Camera(
                camera=camera,
                flag=flag,
                mode =config['camera']['mode'],
                camera_name=config['camera']['name'],
                fps = fps,
                daemon=True
            ).start()

            time.sleep(2)

        sensor_locks = {}
        sensor_names = {}
        sensor_connections = {}

        for i in config['sensors'].keys():
            
            sensors_handler = sh.Handler(config['sensors'][i], local=config['local_development'])
            
            name = config['sensors'][i]['name']

            sensor_connections[name] = sensors_handler.obj
            sensor_locks[name] = threading.Lock()
            sensor_names[name] = name


        tx_queue = None
        tx_lock = None
            
        for i in sensor_connections.keys():
            threads.Sensors(
                conn = sensor_connections[i],
                tx_queue = tx_queue,
                tx_lock = tx_lock,
                sensor_lock = sensor_locks[i],
                flag = flag,
                date = date,
                path = path,
                sensor_name = sensor_names[i],
                daemon=True
            ).start()

        while True:
            pass

    except ServiceExit:
        flag.set()
        camera.video_control()

if __name__ == '__main__':
    main()
