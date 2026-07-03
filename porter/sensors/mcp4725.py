import board
import busio
import time
import logging

import adafruit_mcp4725

logger = logging.getLogger(__name__)

class MCP4725:

    def __init__(self, address=None):
        # Initialize I2C bus.
        i2c = busio.I2C(board.SCL, board.SDA)

        # Initialize MCP4725.
        if address:
            self.dac = adafruit_mcp4725.MCP4725(i2c, address=address)
        else:
            self.dac = adafruit_mcp4725.MCP4725(i2c)

    def configure(self, config):

        bits = 4095
        
        volt = config['voltage']
        
        logger.info(f'Set DAC voltage: {volt}')

        self.dac.raw_value = int(bits*config['voltage']/config['max_voltage'])

    def read_continous_binary(self, fs, flag):
        
        time.sleep(10)
        
