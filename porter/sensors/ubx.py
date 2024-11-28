import logging
import time

import pyubx2 as ubx
import serial

logger = logging.getLogger()


class UBX:

    def __init__(self, port, baudrate, name):

        self.conn = serial.Serial(port, 38400, timeout=1)
        self.name = name

        self.__new_baudrate = False

        if baudrate != 38400:
            self.__new_baudrate = True
            self.__port = port
            self.__brate = int(baudrate)

        if self.conn.is_open:
            logging.info(f"Connected to ublox sensor {self.name} @ {38400}")
            self.reader = ubx.UBXReader(self.conn, protfilter=2)

    def configure(self, config):

        layers = 1
        transaction = 0

        keys = []

        for i in config.keys():

            if i.lower() == "rate":

                rate = int(1 / config["RATE"]["value"] * 1000)
                keys.append(("CFG_RATE_MEAS", rate))

            elif i.lower() == "ubx_msg":

                output_port = config["UBX_MSG"]["output_port"]

                if output_port[0].lower() == "uart":
                    port_string = "UART" + str(int(output_port[1]))
                else:
                    port_string = output_port

                string = "CFG_MSGOUT_UBX_"

                for j in config["UBX_MSG"].keys():
                    if j.lower() == "output_port":
                        pass
                    else:
                        for k in config["UBX_MSG"][j]:
                            msg = string + j + "_" + k + "_" + port_string

                            keys.append((msg, 1))

            elif i.lower() == "nmea_msg":

                output_port = config["NMEA_MSG"]["output_port"]

                if output_port[0].lower() == "uart":
                    port_string = "UART" + str(int(output_port[1]))
                else:
                    port_string = output_port

                string = "CFG_MSGOUT_NMEA_ID"

                for j in config["NMEA_MSG"].keys():
                    if j.lower() == "output_port":
                        pass
                    else:
                        for k in config["NMEA_MSG"][j]:
                            msg = string + "_" + k + "_" + port_string

                            keys.append((msg, 1))

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

        cfgs = ubx.UBXMessage.config_set(layers, transaction, keys)

        msg_count = 0
        ack_count = 0

        for i in range(2):
            count = 0
            msg_cfg_count = 0
            t0 = time.perf_counter()
            if self.conn.inWaiting() == 0 and i == 0:
                self.conn.write(cfgs.serialize())
                msg_count += 1
                msg_cfg_count += 1
                logging.info(
                    f"Sent UBLOX configuration message {cfgs} - Count: {msg_count} {msg_cfg_count}"
                )

            parsed_data = self.read(parsing=True)

            to_read = self.conn.inWaiting()
            logging.info(
                f"Count: {count} - {parsed_data.identity} --- To Read {to_read}"
            )

            if parsed_data.identity == "ACK-ACK":
                ack_count += 1

            while parsed_data.identity != "ACK-ACK":
                parsed_data = self.read(parsing=True)
                to_read = self.conn.inWaiting()
                logging.info(
                    f"Count: {count} - {parsed_data.identity} --- To Read {to_read}"
                )
                if (
                    to_read == 0
                    and parsed_data.identity != "ACK-ACK"
                    and msg_cfg_count != 1
                ):
                    self.conn.write(cfgs.serialize())
                    msg_count += 1
                    msg_cfg_count += 1
                    logging.info(
                        f"Sent UBLOX configuration message {cfgs} - Count: {msg_count} {msg_cfg_count}"
                    )

                if parsed_data.identity == "ACK-ACK":
                    ack_count += 1

                if count >= 30:
                    if msg_cfg_count != 1:
                        self.conn.write(cfgs.serialize())
                        msg_count += 1
                        msg_cfg_count += 1
                        logging.info(
                            f"Sent UBLOX configuration message {cfgs} - Count: {msg_count} {msg_cfg_count}"
                        )
                    break
                count += 1

            while time.perf_counter() - t0 < 1.0:
                pass

        if ack_count == 2:
            logging.info("UBlox Sensor Configured Correctly")

        if self.__new_baudrate:
            t0 = time.perf_counter()
            msg_baud = ubx.UBXMessage.config_set(
                1, 0, [("CFG_UART1_BAUDRATE", self.__brate)]
            )
            self.conn.write(msg_baud.serialize())

            while time.perf_counter() - t0 <= 1.0:
                pass

            del self.reader
            self.conn.close()

            while time.perf_counter() - t0 <= 0.5:
                pass

            self.conn = serial.Serial(self.__port, self.__brate, timeout=1)

            if self.conn.is_open:
                logging.info(f"Connected to ublox sensor {self.name} @ {self.__brate}")

                self.reader = ubx.UBXReader(self.conn)

    def read_continous_binary(self, fs, flag, sensor_lock):

        while not flag.is_set():
            sensor_lock.acquire()
            msg = self.read()
            sensor_lock.release()
            fs.write(msg)

        self.close()

    def read(self, parsing=False):

        raw, parsed = self.reader.read()

        if parsing:
            return parsed
        else:
            return raw

    def close(self):

        self.conn.close()

        logging.info(f"Closed ublox sensor {self.name}")
