import logging
import struct
import time

import smbus2

# ADS1015 registers
ADS1015_REG_CONVERSION = 0x00
ADS1015_REG_CONFIG = 0x01

ADS1015_CONFIG_COMP_QUE = 0b11

# ADS1015 config register fields
ADS1015_CONFIG_MUX = {
    "SINGLE_0": 0b100,
    "SINGLE_1": 0b101,
    "SINGLE_2": 0b110,
    "SINGLE_3": 0b111,
    "DIFF_0_1": 0b000,
    "DIFF_0_3": 0b001,
    "DIFF_1_3": 0b010,
    "DIFF_2_3": 0b011,
}

ADS1015_CONFIG_GAIN = {
    "6.144V": 0b000,
    "4.096V": 0b001,
    "2.048V": 0b010,
    "1.024V": 0b011,
    "0.512V": 0b100,
    "0.256V": 0b101,
}

ADS1015_CONFIG_MODE = {"Continuous": 0b0, "Single-Shot": 0b1}

ADS1015_CONFIG_RATE = {
    "128": 0b000,
    "250": 0b001,
    "490": 0b010,
    "920": 0b011,
    "1600": 0b100,
    "2400": 0b101,
    "3300": 0b110,
    "3300": 0b111,
}

logger = logging.getLogger()

class ADS1015:

    def __init__(self, channel, bus=1, address=0x48, **kwargs):

        self.name = kwargs.get("name", "Generic ADC")

        self.model = kwargs.get("model", "ADS1015")

        self.address = address

        self._gain = ADS1015_CONFIG_GAIN["1.024V"]
        self._rate = ADS1015_CONFIG_RATE["1600"]

        self.__read_mode = kwargs.get("read mode", ADS1015_CONFIG_MODE["Continuous"])

        mode = kwargs.get("mode", "differential")

        if mode.lower() == "differential":
            string = "DIFF_" + str(int(channel[0])) + "_" + str(int(channel[1]))
        else:
            string = "SINGLE_" + str(int(channel))

        self.__mux_channels = ADS1015_CONFIG_MUX[string]

        self.bus = smbus2.SMBus(bus)

        self.__time_sample = 1 / self._rate

        self.__config_register = (
            (self.__mux_channels << 12)
            | (self._gain << 9)
            | (self.__read_mode << 8)
            | (self._rate << 5)
            | (ADS1015_CONFIG_COMP_QUE << 1)
        )

        logger.info(f"Connected to ADC {self.name}")
        logger.info(f"Current Data Rate in s: {self.__time_sample}")
        logger.info(f"Current Gain: {self._gain}")

    def read_continous_binary(self,  fs, flag):

        # Write the config register
        self.bus.write_word_data(self.address, ADS1015_REG_CONFIG, self.__config_register)

        while not flag.is_set():
            msg = struct.pack("<d", time.time())

            tstart = time.perf_counter()

            raw_value = self.bus.read_word_data(self.address, ADS1015_REG_CONVERSION)

            raw_value = ((raw_value << 8) & 0xFF00) | (raw_value >> 8)
            raw_value = (raw_value >> 4) & 0xFFF

            msg += struct.pack('<f', (raw_value * self._gain) / 2**12)

            delta = time.perf_counter() - tstart

            msg += struct.pack("<f", delta)

            fs.write(msg)

            while delta < self.__time_sample:
                delta = time.perf_counter() - tstart
            print(delta, self.__time_sample, self._rate)

    def configure(self, config):

        keys = ["gain", "rate"]

        for i in config.keys():

            if i.lower() == "gain":
                self._gain = ADS1015_CONFIG_GAIN[config[i]]
                logger.info(f"Current Gain: {self._gain}")
            elif i.lower() == "rate":
                self._rate = ADS1015_CONFIG_RATE[config[i]]
                self.__time_sample = 1 / self._rate
                logger.info(f"Current Data Rate in s: {self.__time_sample}")

        self.__config_register = (
            (self.__mux_channels << 12)
            | (self._gain << 9)
            | (self.__read_mode << 8)
            | (self._rate << 5)
            | (ADS1015_CONFIG_COMP_QUE << 1)
        )

    def close(self):

        logging.info(f"Closed sensor {self.name}")
