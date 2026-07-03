import logging
import subprocess
import os
import signal
import time

logger = logging.getLogger(__name__)


class IMX5SensorModule:

    def __init__(self, name="IMX5 Sensors", device="/dev/ttyUSB0", baudrate=115200, model="Various", sensor_core=None):

        self.name = name
        self.model = model
        self.core = sensor_core
        self.device = device
        self.imu_rate = None
        self.ins_rate = None
        self.baudrate = baudrate

        self.process = None

        logger.info(f"Connected to IMX5 sensors {self.name}")

    def read_continous_binary(self, shutdown_flag, datafile_name):
        # Start the IMX5SensorModule process through the command line.
        binary_path = "bin/IMX5SensorModule"

        cmd = f"{binary_path} --imu-rate {self.imu_rate} --ins-rate {self.ins_rate} --baud-rate {self.baudrate} --outputdir {datafile_name} --device {self.device}"
        if self.core is not None:
            cmd += f" --core {int(self.core)}"

        logger.info(f"Running command: {cmd}")
        # print(f"Running command: {cmd}")
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
        # Loop until told to close

        while not shutdown_flag.is_set():
            shutdown_flag.wait(1)

        self.close()

    def configure(self, config):
        self.imu_rate = config.get("imu_data_rate", 1000)
        self.ins_rate = config.get("ins_data_rate", 142)

        logger.info(f"Configured {self.name}")
        logger.info(f"Current IMX5 Sensors Data Rate: {self.imu_rate} Hz")
        logger.info(f"Current IMX5 INS Data Rate: {self.ins_rate} Hz")

    def close(self):

        # Kill the process
        if self.process is not None:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process = None

        logger.info(f"Closed sensor {self.name}")
