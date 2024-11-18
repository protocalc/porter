import logging
import time

import pyubx2 as ubx
import serial

logger = logging.getLogger()


class UBX:

    def __init__(self, port, baudrate, name):

        self.conn = serial.Serial(port, 38400, timeout=1)
        self.name = name

        layer = 1
        transaction = 0
        key = [("CFG_UART1_BAUDRATE", int(baudrate))]
        cfgs = ubx.UBXMessage.config_set(layer, transaction, key)

        self.conn.write(cfgs.serialize())

        time.sleep(0.1)
        self.conn.close()
        time.sleep(0.2)
        self.conn = serial.Serial(port, baudrate, timeout=1)

        if self.conn.is_open:
            logging.info(f"Connected to ublox sensor {self.name}")

    def configure(self, config):

        layers = 1
        transaction = 0

        keys = []
        nmea_keys = []
        ubx_keys = []

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

                            ubx_keys.append((msg, 1))

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

                            nmea_keys.append((msg, 1))

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
        logging.info(f"Sent UBLOX configuration message {cfgs}")
        self.conn.write(cfgs.serialize())

        for i in range(100):
            ack = self.read(parsing=True)
            if not isinstance(ack, str):
                if ack.identity == "ACK-ACK":
                    logging.info("UBLOX sensor configured correctly")
                    break

        for i in range(2):
            if i == 1:
                self.conn.close()

                time.sleep(0.2)

                self.conn = serial.Serial(self.__port, self.__baudrate, timeout=1)
            if len(nmea_keys) > 0:
                time.sleep(0.05)
                cfgs = ubx.UBXMessage.config_set(layers, transaction, nmea_keys)
                logging.info(f"Sent UBLOX configuration message {cfgs}")
                self.conn.write(cfgs.serialize())

                for i in range(100):
                    ack = self.read(parsing=True)
                    if not isinstance(ack, str):
                        if ack.identity == "ACK-ACK":
                            logging.info("UBLOX NMEA output configured correctly")
                            break

            if len(ubx_keys) > 0:
                time.sleep(0.05)
                cfgs = ubx.UBXMessage.config_set(layers, transaction, ubx_keys)
                logging.info(f"Sent UBLOX configuration message {cfgs}")
                self.conn.write(cfgs.serialize())

                for i in range(100):
                    ack = self.read(parsing=True)
                    if not isinstance(ack, str):
                        if ack.identity == "ACK-ACK":
                            logging.info("UBLOX ubx output configured correctly")
                            break

    def read_continous_binary(self, fs, flag):

        while not flag.is_set():
            reader = ubx.UBXReader(self.conn, parsing=False)

            fs.write(reader.read()[0])

        self.close()

    def read(self, parsing=False):
        reader = ubx.UBXReader(self.conn, parsing=parsing)

        raw, parsed = reader.read()

        if parsing:
            return parsed
        else:
            return raw

    def close(self):

        self.conn.close()

        logging.info(f"Closed ublox sensor {self.name}")
