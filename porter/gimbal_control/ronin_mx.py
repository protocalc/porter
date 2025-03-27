import subprocess
import logging
import os
import time

logger = logging.getLogger()

class Gimbal():
    def __init__(self, device, gimbal_name):
        self.name = gimbal_name
        self.device = device

        logger.info(f"Connected to Gimbal {self.name}")

    def maneuver(self, shutdown_flag):
        cmd = f"porter/gimbal_control/./RONIN_MX"
        self.process = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

        while not shutdown_flag.is_set():
            time.sleep(1)

        self.close()

    def close(self):
        if self.process is not None:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process = None

        logger.info(f"Closed gimbal {self.name}")





