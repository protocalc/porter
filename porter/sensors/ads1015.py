import logging
import random
import struct
import time

import lgpio
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

        self.bus = lgpio.i2c_open(bus, address)

        self.__time_sample = 1 / 1600.0

        self.__config_register = (
            ADS1015_REG_CONFIG_CQUE_NONE
            | ADS1015_REG_CONFIG_CLAT_NONLAT
            | ADS1015_REG_CONFIG_CPOL_ACTVLOW
            | ADS1015_REG_CONFIG_CMODE_TRAD
            | self.__read_mode
            | self._rate
            | self._gain
            | self.__mux_channels
            | ADS1015_REG_CONFIG_OS_SINGLE
        )

        self.__read_buffer = bytearray(2)

        logger.info(f"Connected to ADC {self.name}")
        logger.info(f"Current Data Rate in s: {self.__time_sample}")
        logger.info(f"Current Gain: {self._gain}")

    def read_continous_binary(self, fs, flag):

        string = [(self.__config_register >> 8) & 0xFF, self.__config_register & 0xFF]
        # Write the config register

        lgpio.i2c_write_i2c_block_data(self.bus, ADS1015_REG_CONFIG, config_bytes)

        tmsg = time.perf_counter()

        counter = 0
        t = 0

        while not flag.is_set():
            msg = struct.pack("<d", time.time())

            tstart = time.perf_counter()

            # while time.perf_counter()- tmsg < (self.__time_sample+5e-4):
            #    pass
            raw_value = self.bus.i2c_read_i2c_block_data(
                self.address, ADS1015_REG_CONVERSION, 2
            )
            delta0 = time.perf_counter() - tstart
            # raw_value = random.random()

            raw_value = ((raw_value[0] << 8) | (raw_value[1] & 0xFF)) >> 4

            msg += struct.pack("<f", (raw_value * 6.144) / 2048.0)

            delta = time.perf_counter() - tstart

            msg += struct.pack("<f", delta)

            # fs.write(msg)

            while delta < 1e-3:
                delta = time.perf_counter() - tstart
            counter += 1
            t += delta
            print(delta, self.__time_sample, self._rate, counter, t, tstart, delta0)

    def configure(self, config):

        keys = ["gain", "rate"]

        for i in config.keys():

            if i.lower() == "gain":
                print(config[i])
                self._gain = ADS1015_CONFIG_GAIN[str(config[i])]
                logger.info(f"Current Gain: {self._gain}")
            elif i.lower() == "data_rate":
                print("RATE", config[i], i)
                self._rate = ADS1015_CONFIG_RATE[str(config[i])]
                self.__time_sample = 1 / config[i]
                print(self.__time_sample)
                logger.info(f"Current Data Rate in s: {self.__time_sample}")

        print("Gain", self._gain)

        self.__config_register = (
            ADS1015_REG_CONFIG_CQUE_NONE
            | ADS1015_REG_CONFIG_CLAT_NONLAT
            | ADS1015_REG_CONFIG_CPOL_ACTVLOW
            | ADS1015_REG_CONFIG_CMODE_TRAD
            | self.__read_mode
        )
        print("Config 1", self.__config_register, self._rate)
        self.__config_register |= self._rate
        print("Config 2", self.__config_register, self._rate)
        self.__config_register |= self._gain
        print("Config 3", self.__config_register, self.__mux_channels)
        self.__config_register |= self.__mux_channels
        print("Config 4", self.__config_register)
        self.__config_register |= ADS1015_REG_CONFIG_OS_SINGLE
        print("Config 5", self.__config_register)

        print("Config", self.__config_register)

    def close(self):

        logging.info(f"Closed sensor {self.name}")
