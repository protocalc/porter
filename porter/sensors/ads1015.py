import logging
import struct
import time

import smbus2

# ADS1015 registers
ADS1015_REG_CONVERSION = 0x00
ADS1015_REG_CONFIG = 0x01

ADS1015_REG_CONFIG_CQUE_NONE = 0x0003
ADS1015_REG_CONFIG_CLAT_NONLAT = 0x0000
ADS1015_REG_CONFIG_CPOL_ACTVLOW = 0x0000
ADS1015_REG_CONFIG_CMODE_TRAD = 0x0000
ADS1015_REG_CONFIG_OS_SINGLE = 0x8000

# ADS1015 config register fields
ADS1015_CONFIG_MUX = {
    "SINGLE_0": 0x4000,
    "SINGLE_1": 0x5000,
    "SINGLE_2": 0x6000,
    "SINGLE_3": 0x7000,
    "DIFF_0_1": 0x0000,
    "DIFF_0_3": 0x1000,
    "DIFF_1_3": 0x2000,
    "DIFF_2_3": 0x3000,
}

ADS1015_CONFIG_GAIN = {
    "2/3": 0x0000,
    "1": 0x0200,
    "2": 0x0400,
    "4": 0x0600,
    "8": 0x0800,
    "16": 0x0A00,
}

ADS1015_CONFIG_MODE = {"Continuous": 0x0000, "Single-Shot": 0x0100}

ADS1015_CONFIG_RATE = {
    "128": 0x0000,
    "250": 0x0020,
    "490": 0x0040,
    "920": 0x0060,
    "1600": 0x0080,
    "2400": 0x00A0,
    "3300": 0x00C0,
}

logger = logging.getLogger()


class ADS1015:

    def __init__(self, channel, bus=1, address=0x48, **kwargs):

        self.name = kwargs.get("name", "Generic ADC")

        self.model = kwargs.get("model", "ADS1015")

        self.address = address

        self._gain = ADS1015_CONFIG_GAIN["8"]
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
            ADS1015_REG_CONFIG_CQUE_NONE
            | ADS1015_REG_CONFIG_CLAT_NONLAT
            | ADS1015_REG_CONFIG_CPOL_ACTVLOW
            | ADS1015_REG_CONFIG_CMODE_TRAD
            | read_mode
            | self._rate
            | self._gain
            | self.__mux_channels
            | ADS1015_REG_CONFIG_OS_SINGLE
        )

        logger.info(f"Connected to ADC {self.name}")
        logger.info(f"Current Data Rate in s: {self.__time_sample}")
        logger.info(f"Current Gain: {self._gain}")

    def read_continous_binary(self, fs, flag):

        # Write the config register
        self.bus.write_i2c_block_data(
            self.address,
            ADS1015_REG_CONFIG,
            [(self.__config_register >> 8) & 0xFF, self.__config_register & 0xFF],
        )

        while not flag.is_set():
            msg = struct.pack("<d", time.time())

            tstart = time.perf_counter()

            raw_value = self.bus.read_word_data(self.address, ADS1015_REG_CONVERSION, 2)

            raw_value = ((result[0] << 8) | (result[1] & 0xFF)) >> 4

            msg += struct.pack("<f", (raw_value * self._gain) / 2048)

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
            ADS1015_REG_CONFIG_CQUE_NONE
            | ADS1015_REG_CONFIG_CLAT_NONLAT
            | ADS1015_REG_CONFIG_CPOL_ACTVLOW
            | ADS1015_REG_CONFIG_CMODE_TRAD
            | read_mode
            | self._rate
            | self._gain
            | self.__mux_channels
            | ADS1015_REG_CONFIG_OS_SINGLE
        )

    def close(self):

        logging.info(f"Closed sensor {self.name}")
