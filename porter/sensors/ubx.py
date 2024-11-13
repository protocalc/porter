import logging

import pyubx2 as ubx
import serial

logger = logging.getLogger()


class UBX:

    def __init__(self, port, baudrate, name):

        self.conn = serial.Serial(port, baudrate, timeout=1)
        self.name = name

        if self.conn.is_open:
            logging.info(f"Connected to ublox sensor {self.name}")

    def configure(self, config):

        layers = 1
        transaction = 0

        keys = []

        for i in config.keys():
			
            print(i)

            if i.lower() == "rate":

                time = int(1 / config["RATE"]["value"] * 1000)
                keys.append(("CFG_RATE_MEAS", time))

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

            elif i.lower() == "nmea" or i.lower() == "ubx":

                if config[i]["output"]["set"]:
                    output = 1
                else:
                    output = 0

                string = "CFG_" + config[i]["output"]["port"] + "OUTPROT_" + i

                keys.append((string, output))

            else:
                print('ok', i)
                if isinstance(config[i], list):
                    keys.append([config[i][0], config[i][1]])
        print('end', keys)
        cfgs = ubx.UBXMessage.config_set(layers, transaction, keys)

        self.conn.write(cfgs.serialize())

        ack = self.read(parsing=True)

        print(ack)

        if ack.identity == "ACK-ACK":
            logging.info("UBLOX sensor configured correctly")

    def read_continous_binary(self, fs, flag):

        while not flag.is_set():
            reader = ubx.UBXReader(self.conn, parsing=False)

            fs.write(reader.read()[0])

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
        logging.info(f"Closed ublox sensor {self.name}")
