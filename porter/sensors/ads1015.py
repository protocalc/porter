import logging
import random
import struct
import time

import lgpio

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

ADS1015_VALUE_GAIN = {
    "2/3": 6.144,
    "1": 4.096,
    "2": 2.048,
    "4": 1.024,
    "8": 0.512,
    "16": 0.256,
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
        self._gain_value = ADS1015_VALUE_GAIN["8"]
        self._rate = ADS1015_CONFIG_RATE["1600"]

        self.__read_mode = kwargs.get("read mode", ADS1015_CONFIG_MODE["Continuous"])

        mode = kwargs.get("mode", "differential")

        if mode.lower() == "differential":
            string = "DIFF_" + str(int(channel[0])) + "_" + str(int(channel[1]))
        else:
            string = "SINGLE_" + str(int(channel))

        self.__mux_channels = ADS1015_CONFIG_MUX[string]

        self.bus = lgpio.i2c_open(bus, address)

        self.__adc_sample = 1 / 1600.0
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
        logger.info(f"Current ADC Data Rate in s: {self.__adc_sample}")
        logger.info(f"Current Reading Data Rate in s: {self.__time_sample}")
        logger.info(f"Current Gain: {self._gain_value}")

    def read_continous_binary(self, fs, flag):

        config_bytes = [
            (self.__config_register >> 8) & 0xFF,
            self.__config_register & 0xFF,
        ]
        lgpio.i2c_write_i2c_block_data(self.bus, ADS1015_REG_CONFIG, config_bytes)

        msg_buffer = bytearray(20)

        count = 0
        avg_read_time = 0

        next_sample_time = time.perf_counter_ns()

        while not flag.is_set():

            t_start = time.perf_counter_ns()

            _, raw_value = lgpio.i2c_read_i2c_block_data(
                self.bus, ADS1015_REG_CONVERSION, 2
            )

            raw_value = ((raw_value[0] << 8) | (raw_value[1] & 0xFF)) >> 4

            read_time = time.perf_counter_ns() - t_start

            struct.pack_into("<d", msg_buffer, 0, time.time())
            struct.pack_into("<q", msg_buffer, 8, read_time)
            struct.pack_into("<f", msg_buffer, 16, (raw_value * self._gain) / 2048)

            next_sample_time = next_sample_time + self.__time_sample * (
                1 + int(read_time / self.__time_sample)
            )

            fs.write(msg_buffer)

            while time.perf_counter_ns() < next_sample_time:
                pass

        self.close()

    def configure(self, config):

        keys = ["gain", "ADC_rate", ""]

        for i in config.keys():

            if i.lower() == "gain":
                self._gain = ADS1015_CONFIG_GAIN[str(config[i])]
                self._gain_value = ADS1015_VALUE_GAIN[str(config[i])]

                logger.info(f"Current Gain: {self._gain_value}")
            elif i.lower() == "adc_rate":
                self._rate = ADS1015_CONFIG_RATE[str(config[i])]
                self.__adc_sample = 1 / config[i]

                logger.info(f"Current ADC Data Rate in s: {self.__adc_sample}")

            elif i.lower() == "reading_rate":
                self._rate = ADS1015_CONFIG_RATE[str(config[i])]
                self.__time_sample = 1 / config[i]

                if self.__time_sample < self.__adc_sample:
                    self.__time_sample = self.__adc_sample * 1.5
                    logger.info(f"Set Reading Data Rate in s: {self.__time_sample}")
                else:
                    logger.info(f"Current Reading Data Rate in s: {self.__time_sample}")

        self.__config_register = (
            ADS1015_REG_CONFIG_CQUE_NONE
            | ADS1015_REG_CONFIG_CLAT_NONLAT
            | ADS1015_REG_CONFIG_CPOL_ACTVLOW
            | ADS1015_REG_CONFIG_CMODE_TRAD
            | self.__read_mode
        )

        self.__config_register |= self._rate
        self.__config_register |= self._gain
        self.__config_register |= self.__mux_channels
        self.__config_register |= ADS1015_REG_CONFIG_OS_SINGLE

    def close(self):

        logging.info(f"Closed sensor {self.name}")
