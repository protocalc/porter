import logging
import subprocess
import os
import signal
import time

logger = logging.getLogger()


class LM76SensorModule:

    def __init__(
        self,
        name="LM76 Temperature Sensor",
        bus="/dev/i2c-1",
        address="0x4B",
        model="LM76",
        sensor_core=None,
    ):

        self.name = name
        self.model = model
        self.core = sensor_core
        self.bus = bus
        self.address = address
        self.interval = 10  # Default to 10 seconds
        self.tcrit = None
        self.thyst = None
        self.tlow = None
        self.thigh = None

        self.process = None

        logger.info(f"Connected to LM76 sensor {self.name}")

    def read_continous_binary(self, shutdown_flag, datafile_name):
        # Start the LM76SensorModule process through the command line.
        # Find the binary relative to this script's location
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        binary_path = os.path.join(script_dir, "build", "bin", "LM76SensorModule")

        cmd = f"{binary_path} --bus {self.bus} --address {self.address} --interval {self.interval}"
        
        # Add threshold configurations if set
        if self.tcrit is not None:
            cmd += f" --tcrit {self.tcrit}"
        if self.thyst is not None:
            cmd += f" --thyst {self.thyst}"
        if self.tlow is not None:
            cmd += f" --tlow {self.tlow}"
        if self.thigh is not None:
            cmd += f" --thigh {self.thigh}"
        
        if self.core is not None:
            cmd += f" --core {int(self.core)}"

        logger.info(f"Running command: {cmd}")
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            preexec_fn=os.setsid,
        )
        # Loop until told to close

        while not shutdown_flag.is_set():
            time.sleep(1)

        self.close()

    def configure(self, config):
        self.interval = config.get("interval", 1)
        self.tcrit = config.get("tcrit", None)
        self.thyst = config.get("thyst", None)
        self.tlow = config.get("tlow", None)
        self.thigh = config.get("thigh", None)

        logger.info(f"Configured {self.name}")
        logger.info(f"Current LM76 Reading Interval: {self.interval} seconds")
        if self.tcrit is not None:
            logger.info(f"T_CRIT threshold: {self.tcrit}°C")
        if self.thyst is not None:
            logger.info(f"THYST threshold: {self.thyst}°C")
        if self.tlow is not None:
            logger.info(f"TLOW threshold: {self.tlow}°C")
        if self.thigh is not None:
            logger.info(f"THIGH threshold: {self.thigh}°C")

    def close(self):

        # Kill the process
        if self.process is not None:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process = None

        logger.info(f"Closed sensor {self.name}")

