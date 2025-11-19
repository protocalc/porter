import logging
import random
import struct
import time
import array
import queue
import subprocess
import os
import signal

logger = logging.getLogger()

class Inertial:

    def __init__(self, name="Inertial Sensors", bus=4, model="Various", sensor_core=None):

        self.name = name 
        self.model = model 
        self.core = sensor_core
        self.bus = int(bus)
        self.rate = None

        self.process = None

        logger.info(f"Connected to inertial sensors {self.name}")

    def read_continous_binary(self, shutdown_flag, datafile_name):
        # Start the inertial process through the command line.
        cmd = f"bin/inertial --rate {self.rate} --outputdir {datafile_name} --i2c-bus {self.bus}"
        if self.core is not None:
            cmd += f" --core {int(self.core)}"
            
        # print(f"Running command: {cmd}")
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid) 
        # Loop until told to close

        while not shutdown_flag.is_set():
            time.sleep(1)

        self.close()

    def configure(self, config):
        self.rate = config.get("data_rate", 200)

        logger.info(f"Configured {self.name}")
        logger.info(f"Current Inertial Sensors Data Rate: {self.rate} Hz")

    def close(self):

        # Kill the process
        if self.process is not None:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process = None

        logger.info(f"Closed sensor {self.name}")
