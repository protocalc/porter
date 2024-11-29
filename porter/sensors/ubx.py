import logging
import queue
import time

import pyubx2 as ubx
import serial

logger = logging.getLogger()


class UBX:

    def __init__(self, port, baudrate, name):

        self.name = name

        self.__new_baudrate = False

        self.__msg_received = 0
        self.__msg_written = 0

        self.config_queue = queue.Queue()

        self.conn = serial.Serial(port, 38400, timeout=1)
        if self.conn.is_open:
            logging.info(f"Open Connection to UBlox sensor {self.name} @ {38400}")
            self.reader = ubx.UBXReader(self.conn, protfilter=2)

        if baudrate != 38400:
            self.__new_baudrate = True
            self.__port = port
            self.__brate = int(baudrate)

    def read_data(self, reading_queue, sensor_lock):

        if self.conn.inWaiting():
            sensor_lock.acquire()
            (raw, parsed) = self.reader.read()
            sensor_lock.release()

            if parsed_data is not None:
                self.__msg_received += 1
                self.reading_queue.put((raw, parsed))

    def write_data(self, writing_queue, sensor_lock, timeout=1.0):

        msg_count = 0

        while not writing_queue.empty():

            msg = writing_queue.get(False)

            sensor_lock.acquire()
            self.conn.write(msg[1].serialize())
            sensor_lock.release()

            if msg[0] == "CFG":
                logging.info(
                    f"Sent UBLOX configuration message {msg[1]} - Count: {msg_count}"
                )
                msg_count += 1

                while time.perf_counter() - t0 < timeout:
                    pass

            elif msg[0] == "BAUD":
                self.conn.write(msg[1].serialize())

                while time.perf_counter() - t0 <= timeout:
                    pass

                del self.reader
                self.conn.close()

                while time.perf_counter() - t0 <= 0.5:
                    pass

                self.conn = serial.Serial(self.__port, self.__brate, timeout=0.1)

                if self.conn.is_open:
                    logging.info(
                        f"Connected to ublox sensor {self.name} @ {self.__brate}"
                    )

                    self.reader = ubx.UBXReader(self.conn)

    def save_data(self, reading_queue, filename):

        ack_count = 0
        msg_skipped = 0
        stop_counter = False

        while not reading_queue.empty():
            raw, parsed = reading_queue.get(False)
            if not stop_counter:
                msg_skipped += 1

            if parsed.identity == "ACK-ACK":
                ack_count += 1
                logging.info(f"Message {parsed} @ acknolwedged")

            if ack_count >= 2:
                if not stop_counter:
                    logging.info(f"Skipped {msg_skipped} messages")
                stop_counter = True
                if parsed.identity != "ACK-ACK":
                    filename.write(raw)

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
        serial_cfgs = cfgs.serialize()

        self.config_queue.put(("CFG", serial_cfgs))
        self.config_queue.put(("CFG", serial_cfgs))

        if self.__new_baudrate:

            baud_cfgs = ubx.UBXMessage.config_set(
                1, 0, [("CFG_UART1_BAUDRATE", self.__brate)]
            )

            self.config_queue.put(("BAUD", baud_cfgs.serialize()))

    def close(self):

        self.conn.close()

        logging.info(f"Closed ublox sensor {self.name}")
