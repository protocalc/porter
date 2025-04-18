import logging
import time
from datetime import datetime
import io

import pyubx2 as ubx

import serial


logger = logging.getLogger("mainlogger")

HEADER = b"\xb5\x62"


def find_baudrate(port, logger, baudrates=[38400, 57600, 115200, 230400], timeout=1.0):

    brate_found = False

    for brate in baudrates:

        if brate_found:
            pass
        else:
            conn = serial.Serial(port, brate, timeout=timeout)
            logger.info(f"Attempting Baudrate {brate}")
            conn.read(conn.inWaiting())
            poll = ubx.UBXMessage("MON", "MON-VER", ubx.POLL)
            conn.reset_input_buffer()
            print(conn.inWaiting())
            conn.write(poll.serialize())

            data = conn.read(1000)
            i = 0
            while i < 998:
                if data[i : i + 2] == b"\xb5\x62":
                    print(data[i : i + 2])
                    logger.info(f"Found Baudrate @ {brate}")
                    reader = ubx.UBXReader(io.BytesIO(data))
                    res, parsed = reader.read()
                    logger.info(f"{type(parsed.identity)} ---- {parsed.identity}")
                    brate_found = True
                    i = 10000
                    break

                i += 1

            conn.read(conn.inWaiting())
            conn.close()
            time.sleep(0.2)

    return brate


class UBX:

    def __init__(self, port, baudrate, name):

        self.name = name

        self.__new_baudrate = False

        if baudrate != 38400:
            # Set parameters for updating baudrate of the GPS.
            self.__new_baudrate = True
            self.__port = port
            self.__brate = int(baudrate)

        else:
            # Open a serial connection with the ZED-F9P at the default baud rate if not configured otherwise.
            self.conn = serial.Serial(port, 38400, timeout=1)
            if self.conn.is_open:
                logger.info(f"Connected to ublox sensor {self.name} @ {38400}")
                self.reader = ubx.UBXReader(self.conn, protfilter=2)

        self.timing_results = ""
        self.identities = ""

    def configure(self, config):

        layers = 1
        transaction = 0

        keys = []

        # Parsing yaml config file keys and converting them to configuration keys that the ZED-F9P can interpret.

        for i in config.keys():

            if i.lower() == "rate":

                # Add rate configuration
                rate = int(1 / config["RATE"]["value"] * 1000)
                keys.append(("CFG_RATE_MEAS", rate))

            elif i.lower() == "ubx_msg":

                # Add output port for UBX messages.
                output_port = config["UBX_MSG"]["output_port"]

                if output_port[0].lower() == "uart":
                    port_string = "UART" + str(int(output_port[1]))
                else:
                    port_string = output_port

                string = "CFG_MSGOUT_UBX_"

                # Enable options for logging different UBX messages.
                for j in config["UBX_MSG"].keys():
                    if j.lower() == "output_port":
                        pass
                    else:
                        for k in config["UBX_MSG"][j]:
                            msg = string + j + "_" + k + "_" + port_string

                            keys.append((msg, 1))

            elif i.lower() == "nmea_msg":

                # Add output port for NMEA messages.
                output_port = config["NMEA_MSG"]["output_port"]

                if output_port[0].lower() == "uart":
                    port_string = "UART" + str(int(output_port[1]))
                else:
                    port_string = output_port

                string = "CFG_MSGOUT_NMEA_ID"

                # Enable options for logging different NMEA messages.
                for j in config["NMEA_MSG"].keys():
                    if j.lower() == "output_port":
                        pass
                    else:
                        for k in config["NMEA_MSG"][j]:
                            msg = string + "_" + k + "_" + port_string

                            keys.append((msg, 1))

            # Configuring output port configurations for the ZED-F9P
            elif i[:4].lower() == "nmea" or i[:3].lower() == "ubx":

                if i[:4].lower() == "nmea":
                    p = i[:4]
                else:
                    p = i[:3]

                if config[i]["output"]["set"]:
                    output = 1
                else:
                    output = 0

                string = "CFG_" + config[i]["output"]["port"] + "OUTPROT_" + p

                keys.append((string, output))

            else:
                if isinstance(config[i], list):
                    keys.append((config[i][0], config[i][1]))

        # Setting up and serialize the configuration parameters for the ZED-F9P
        cfgs = ubx.UBXMessage.config_set(layers, transaction, keys)
        serial_cfgs = cfgs.serialize()

        # msg_count = 0
        # ack_count = 0

        # if self.__new_baudrate:
        # # Open a serial connection at default baudrate of ZED-F9P to ensure connectivity upon reboot.
        # self.conn = serial.Serial(self.__port, 38400, timeout=1)
        # if self.conn.is_open:
        # logger.info(f"Connected to ublox sensor {self.name} @ {38400}")
        # self.reader = ubx.UBXReader(self.conn, protfilter=2)

        # self.conn.reset_input_buffer()
        # self.conn.write(serial_cfgs)

        # t0 = time.perf_counter()
        # while time.perf_counter() - t0 <= 1.0:
        # parsed = self.read(parsing=True)
        # if parsed.identity == "ACK-ACK":
        # logger.info(f"Output Configuration ACK {parsed.identity}")
        # logger.info(f"Configuration {keys}")
        # break
        # else:
        # logger.info(f"Output Configuration {parsed.identity}")

        # logger.info(
        # f"Output Configuration ACK {parsed.identity} {time.perf_counter() - t0}"
        # )
        # logger.info(f"Configuration {keys}")

        if self.__new_baudrate:
            # self.conn.reset_input_buffer()

            # del self.reader
            # self.conn.close()
            # Set the ZED-F9P baudrate to the one specified in the config file.
            msg_baud = ubx.UBXMessage.config_set(
                1, 0, [("CFG_UART1_BAUDRATE", self.__brate)]
            )

            time.sleep(0.5)

            baudrate_temp = 0

            count = 0
            loops = 10

            while count < loops:
                baudrate_temp = find_baudrate(self.__port, logger)

                if baudrate_temp == self.__brate:
                    logger.info(f"Correct baudrate found @ {baudrate_temp}")
                    logger.info("Baudrate has been changed correctly")
                    count = 15
                    break

                self.conn = serial.Serial(self.__port, baudrate_temp, timeout=1)
                self.conn.write(msg_baud.serialize())

                logger.info(
                    f"Baudrate Message written with current Baudrate @ {baudrate_temp}"
                )
                time.sleep(0.2)

                t0 = time.perf_counter()
                while time.perf_counter() - t0 <= 1.0:
                    self.conn.reset_input_buffer()

                self.conn.close()
                time.sleep(0.2)

                count += 1

            if count >= loops:
                self.__brate = baudrate_temp
                logger.info(f"Baudrate Set @ {self.__brate}")

            time.sleep(0.5)

            # Reopen a serial connection at the new baudrate.
            self.conn = serial.Serial(self.__port, self.__brate, timeout=1)

            if self.conn.is_open:
                logger.info(f"Connected to ublox sensor {self.name} @ {self.__brate}")

                self.reader = ubx.UBXReader(self.conn, protfilter=2)

            self.conn.write(serial_cfgs)
            t0 = time.perf_counter()
            self.conn.read(self.conn.inWaiting())

            while time.perf_counter() - t0 <= 1.0:
                logger.info(f"Bytes  === {self.conn.inWaiting()}")
                parsed = self.read(parsing=True)
                if parsed.identity == "ACK-ACK":
                    logger.info(f"Output Configuration ACK {parsed.identity}")
                    logger.info(f"Configuration {keys}")
                    break
                else:
                    logger.info(f"Output Configuration {parsed.identity}")
            logger.info(
                f"Output Configuration ACK {parsed.identity} {time.perf_counter() - t0}"
            )
            logger.info(f"Configuration {keys}")

    def read_continous_binary(self, shutdown_flag, datafile_name):

        # Capture loop start time for logging printouts.
        loop_start = time.time()
        t_prev = loop_start

        try:
            datafile = open(datafile_name, "r+b")
        except FileNotFoundError:
            datafile = open(datafile_name, "x+b")

        # data_path = '/'.join(datafile_name.split('/')[:-1])

        # timing_path = data_path + '/gps_timing.txt'

        # logger.info(f'Timing path : {timing_path}')

        while not shutdown_flag.is_set():
            # Read from the GPS and measure the amount of time taken.
            t_start = time.perf_counter_ns()
            msg, parsed = self.read(parsing=None)
            t_end = time.perf_counter_ns()

            read_time = t_end - t_start
            t = time.time()

            # Push the data to the queue
            datafile.write(msg)

            # Logging timestamp and GPS messages
            # print_time = datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S.%f")
            # self.timing_results += f"{print_time} {read_time / 1e6} {(t - t_prev) * 1e3} \n"

            # t_prev = t
            # current_time = time.time()

            # Write to output file
            # if current_time - loop_start >= 3600:
            # with open(timing_path, 'w') as f:
            #    f.write(self.timing_results)
            # break

        self.close()

    def read(self, parsing=False):

        # Read from the UBX reader
        raw, parsed = self.reader.read()

        if parsing is None:
            return raw, parsed
        elif parsing:
            return parsed
        else:
            return raw

    def close(self):

        # Turn off the serial connection
        self.conn.close()

        logger.info(f"Closed ublox sensor {self.name}")
