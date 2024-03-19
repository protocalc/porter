import pyubx2 as ubx
import serial
import logging

logger = logging.getLogger()


class UBX:

    def __init__(self, port, baudrate, name):

        self.conn = serial.Serial(port, baudrate, timeout=1)

        if self.conn.is_open:
            logging.info(f"Connected to ublox sensor {name}")

    def configure(self, config):

        layers = 1
        transaction = 0

        keys = []

        for i in config.keys():

            if i.lower() == "rate":

                time = int(1 / config["RATE"]["value"] * 1000)
                keys.append([("CFG_RATE_MEAS", time)])

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

                            keys.append([msg, 1])

            elif i.lower() == "nmea" or i.lower() == "ubx":

                if config[i]["output"]["set"]:
                    output = 1
                else:
                    output = 0

                string = "CFG_" + config[i]["output"]["port"] + "OUTPROT_" + i

                keys.append([(string, output)])

            else:
                if isinstance(config[i], list):
                    keys.append([config[i][0], config[i][1]])

        cfgs = ubx.UBXMessage.config_set(layers, transaction, keys)

        self.conn.write(cfgs.serialize())

        ack = self.read(parsing=True)

        if ack.identity == "ACK-ACK":
            logging.info("UBLOX sensor configured correctly")

    def read(self, parsing=False):

        raw, parsed = ubx.UBXReader(self.conn, parsing=parsing)

        if parsing:
            return parsed
        else:
            return raw

    def close(self):

        self.conn.close()

        logging.info(f"Closed ublox sensor {self.name}")
