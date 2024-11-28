import board
import busio
import time

import adafruit_mcp4725



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
        
        print(int(bits*config['voltage']/config['max_voltage']))

        self.dac.raw_value = int(bits*config['voltage']/config['max_voltage'])

    def read_continous_binary(self, fs, flag, sensor_lock):
        
        time.sleep(10)
        
