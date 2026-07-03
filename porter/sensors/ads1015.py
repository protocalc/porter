import logging
import time
import subprocess
import os
import signal

ADS1015_VALUE_GAIN = {
    1: 4.096,
    2: 2.048,
    4: 1.024,
    8: 0.512,
    16: 0.256,
}

logger = logging.getLogger(__name__)

class ADS1015:

    def __init__(self, name="Generic ADC", bus=6, model="ADS1015", sensor_core=None):
        self.name = name 
        self.model = model 
        self.core = sensor_core
        self.bus = int(bus)

        self.gain = None
        self.rate = None
        self.gain_value = None

        self.process = None

        logger.info(f"Connected to ADC {self.name}")

    def read_continous_binary(self, shutdown_flag, datafile_name):
        # Start the ads1015 process through the command line.
        cmd = f"ads1015 --gain {self.gain} --rate {self.rate} --output {datafile_name} --i2c-bus {self.bus}"
        if self.core is not None:
            cmd += f" --core {int(self.core)}"
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid) 
        # Loop until told to close

        while not shutdown_flag.is_set():
            shutdown_flag.wait(1)

        self.close()

    def configure(self, config):
        self.gain = config.get("gain", 8)
        self.rate = config.get("data_rate", 1600)
        self.gain_value = ADS1015_VALUE_GAIN[self.gain] 

        logger.info(f"Configured {self.name}")
        logger.info(f"Current ADC Data Rate: {self.rate} Hz")
        logger.info(f"Current Gain Setting {self.gain}: {self.gain_value}")

    def close(self):

        # Kill the process
        if self.process is not None:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process = None

        logger.info(f"Closed sensor {self.name}")
