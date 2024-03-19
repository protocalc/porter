import time
import yaml
import sensors.KERNEL as KERNEL

import datetime
import os

path = os.path.dirname(os.path.realpath(__file__))
date = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

cfg_path = path+'/config/calib_config.yml'

with open(cfg_path, 'r') as cfg:
    config = yaml.safe_load(cfg)

sensor_params = config['sensors']['Inclinometer_1']


conn = KERNEL.KernelInertial(
    sensor_params['connection']['parameters']['port'],
    sensor_params['connection']['parameters']['baudrate'],
    name = sensor_params['name']
    )

conn.configure(sensor_params['configuration'])

for i in range(10):

    print(conn.conn.read(10))
