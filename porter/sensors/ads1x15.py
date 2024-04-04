# https://learn.adafruit.com/adafruit-4-channel-adc-breakouts/python-circuitpython
# https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15
# https://www.adafruit.com/product/1085

import logging
import struct
import time

import board
import busio
import numpy as np
from adafruit_ads1x15.analog_in import AnalogIn


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class InputError(Error):
    """Exception raised for errors in the input."""

    errors = {1001: "Choosen input not available"}


MODES = ["differential", "single"]


class Ads1x15:

    def __init__(self, chan_input, pins=None, address=0x48, **kwargs):
        """Interface for the ADS1x15 series of analog-to-digital converters

        Create a connection using I2C protocol to the ADS1115. Requires: -
        chan_input: a list or an int. The channel number input cannot
                      be bigger than 3. If the input is an int, the mode is
                      automatically switched to single. For differential mode
                      the input list needs to have a shape Nx2 where N are the
                      number of differential measurements and each one needs to
                      have 2 channels for the differential measurement e.g.
                      [[0,1],[2,3]] creates two differential measurments, one
                      between the 0 and 1 channel and the other between the 2
                      and 3
        Optional: - mode: possible between differential or single. Check the
        manual for the difference
        """

        mode = kwargs.get("mode", "differential")
        name = kwargs.get("name", "Generic ADC")

        model = kwargs.get("model", "ADS1015")

        self.output_mode = kwargs.get("output_mode", "value")

        try:
            if mode in MODES:
                pass
            else:
                raise InputError(1001)
        except InputError as err:
            print(
                "Error %d: %s, availables modes %s"
                % (err.args[0], err.errors[err.args[0]], MODES)
            )

        if not pins:
            scl = board.SCL
            sda = board.SDA
        else:
            scl = pins["SCL"]
            sda = pins["SCA"]

        ### Connect to the ADC
        i2c = busio.I2C(scl, sda)

        if model == "ADS1015":
            import adafruit_ads1x15.ads1015 as adc

            self.ads = adc.ADS1015(i2c, address)
        else:
            import adafruit_ads1x15.ads1115 as adc

            self.ads = adc.ADS1115(i2c, address)

        channels = [adc.P0, adc.P1, adc.P2, adc.P3]

        if isinstance(chan_input, int) or isinstance(chan_input, float):
            try:
                if chan_input < len(channels):
                    chan_input = [int(chan_input)]
                    mode = "single"
                else:
                    raise InputError(1001)
            except InputError as err:
                logging.error(
                    "Error %d: %s, Input channel in Single Mode higher than the max channel = %d"
                    % (err.args[0], err.errors[err.args[0]], len(channels))
                )
        else:
            try:
                if max(sum(chan_input, [])) > len(channels):
                    raise InputError(1001)
                else:
                    pass
            except InputError as err:
                logging.error(
                    "Error %d: %s, At least a channel in Differential Mode higher than the max channel = %d"
                    % (err.args[0], err.errors[err.args[0]], len(channels))
                )

        self.chan = []

        if mode == "single":
            for i in chan_input:
                self.chan.append(AnalogIn(self.ads, channels[int(i)]))
        else:
            for i in chan_input:
                self.chan.append(
                    AnalogIn(self.ads, channels[int(i[0])], channels[int(i[1])])
                )

        self.__time_sample = 1 / self.ads.data_rate

        logging.info(f"Connected to ADC {name}")

    def read(self, chunk_size=None, return_binary=True):

        count = 0

        if return_binary:
            msg = b""
        else:
            msg = []

        bytes_per_msg = 16

        if not chunk_size:
            chunk_size = bytes_per_msg

        while count <= chunk_size / bytes_per_msg:
            t = time.time()

            if return_binary:
                t = struct.pack("<d", t)

            msg += t

            if self.output_mode == "value":
                msg += self._get_value()
            else:
                msg += self._get_voltage()

            time_last_sample = time.time()

            if return_binary:
                (t,) = struct.unpack("<d", t)

            if time_last_sample - t < self.__time_sample:
                time.sleep(self.__time_sample - (time.time() - t))

            count += 1

        return msg

    def close(self):

        logging.info(f"Closed sensor {self.name}")

    def _get_value(self, return_binary=True):
        """
        Get the RAW value from the ADC
        """

        if return_binary:
            msg = b""
        else:
            msg = []

        for i in self.chan:

            if return_binary:
                msg += struct.pack("<Q", i.value)
            else:
                msg.append(i.value)

        return msg

    def _get_voltage(self, return_binary=True):
        """
        Get the converted voltage from the ADC
        """

        if return_binary:
            msg = b""
        else:
            msg = []

        for i in self.chan:

            if return_binary:
                msg += struct.pack("<d", i.voltage)
            else:
                msg.append(i.voltage)

        return msg

    def stream_data(
        self, samples=None, save=False, filename="adc_values.txt", update_time=None
    ):
        """
        stream and optionally save the data from the adc
        Optional:
        - samples: int, number of values read from the ADC.
                   if None the cycle continues unless is stopped using CTRL+C
        - save: if true data are saved on file
        - filename: name of the file where the data are saved. It is necessary
                    to include path if you want to save the file in a different
                    directory than the working one
        - update_time: float number in ms. if None the data are updated as
                       fast as possible
        """

        def list_sum(data):
            flat_data = [y for x in data for y in (x if isinstance(x, list) else [x])]
            my_sum = flat_data[0]
            for v in flat_data[1:]:
                my_sum += v
            return my_sum

        if update_time is not None:
            update_time = update_time * 1e-3

        count = 0

        adc_count = self.get_value()
        voltage = self.get_voltage()
        t = time.time()

        col_0 = "{:15s}  | ".format("CTime (s)")
        col_1 = []
        col_2 = []

        for k in range(int(np.size(adc_count))):
            if k == int(np.size(adc_count) - 1):
                if self.ads.gain > 8:
                    col_2 = "{:15s}  |  {:15s}  | \n ".format(
                        "ADC Count " + str(int(k)), "Voltage " + str(int(k)) + " (mV)"
                    )
                    fact = 1e3
                else:
                    col_2 = "{:15s}  |  {:15s}  | \n ".format(
                        "ADC Count " + str(int(k)), "Voltage " + str(int(k)) + " (V)"
                    )
                    fact = 1
            else:
                if self.ads.gain > 8:
                    col_1.append(
                        "{:15s}  |  {:15s}  | ".format(
                            "ADC Count " + str(int(k)),
                            "Voltage " + str(int(k)) + " (mV)",
                        )
                    )
                    fact = 1e3
                else:
                    col_1.append(
                        "{:15s}  |  {:15s}  | ".format(
                            "ADC Count " + str(int(k)),
                            "Voltage " + str(int(k)) + " (V)",
                        )
                    )
                    fact = 1

        if len(col_1) > 1:
            col_1 = list_sum(col_1)
            colums_name = col_0 + col_1 + col_2

        elif len(col_1) == 1:
            col_1 = str(col_1[0])
            colums_name = col_0 + col_1 + col_2
        else:
            colums_name = col_0 + col_2

        if save:
            with open(filename, "a") as f:
                f.write(colums_name)

        t = -np.inf

        while True:
            if update_time is not None:
                if time.time() - t < update_time:
                    time.sleep(update_time - time.time() + t)

            adc_count = np.array(self.get_value())
            voltage = np.array(self.get_voltage()) * fact
            t = time.time()

            x = "{:15.0f} |".format(t)
            y = []
            z = []
            for i in range(int(np.size(adc_count))):
                if i == int(np.size(adc_count) - 1):
                    z = "{:15.4f} | {:15.9f} \n".format(adc_count[i], voltage[i])
                else:
                    y.append("{:15.4f} | {:15.9f} |".format(adc_count[i], voltage[i]))

            if np.size(y) > 1:
                y = list_sum(y)
                x = x + y + z
            elif np.size(y) == 1:
                y = str(y)
                x = x + y + z
            else:
                x = x + z
            print(x)

            if save:
                with open(filename, "a") as f:
                    f.write(x)

            if samples is not None:
                count += 1
                if count > samples:
                    break

    def configure(self, config):
        """
        Wrapper function to set parameters of one of the *set* methods
        of this class
        Paramters:
        - cat: str, category of the value that needs to be changed
        - value: float, new value to be set
        """

        for i in config.keys():
            cat = str(i)
            value = config[i]

            if cat.lower() == "gain":
                self.set_gain(value)
            elif cat.lower() == "data_rate":
                self.set_data_rate(value)

    def write(self, msg):

        config = {}

        config[msg[:3].decode("utf-8")] = float(msg[3:].decode())
        self.configure(config)

    def set_gain(self, gain):
        """
        The ADS1115 has the these gain options.

                   GAIN    RANGE (V)
                  ----    ---------
                   2/3    +/- 6.144
                   1      +/- 4.096
                   2      +/- 2.048
                   4      +/- 1.024
                   8      +/- 0.512
                   16     +/- 0.256
        """

        self.ads.gain = gain

    def set_data_rate(self, data_rate):
        """
        Set the data rate of the ADC in Sample per Seconds.
        Available rates: 8, 16, 32, 64, 128, 250, 475, 860
        Requires:
        - data_rates: an integer value to be choosen between the availables one
                      If the choosen value is not available, the closest values
                      is automatically set
        """

        available_rates = [8, 16, 32, 64, 128, 250, 475, 860]

        data_rate = int(data_rate)

        if data_rate not in available_rates:
            (idx,) = np.where(
                np.abs(available_rates - data_rate)
                == np.amin(np.abs(available_rates - data_rate))
            )

            data_rate = available_rates[idx]

        self.ads.mode = Mode.CONTINUOUS
        self.ads.data_rate = data_rate

        self.__time_sample = 1 / self.ads.data_rate
