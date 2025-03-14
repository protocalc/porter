import logging
import time
from datetime import datetime

import pyubx2 as ubx
import serial
import pickle

logger = logging.getLogger()


class UBX:

    def __init__(self, port, baudrate, name):

        self.name = name

        self.__new_baudrate = False

        if baudrate != 38400:
            self.__new_baudrate = True
            self.__port = port
            self.__brate = int(baudrate)

        else:
            self.conn = serial.Serial(port, 38400, timeout=1)
            if self.conn.is_open:
                logging.info(f"Connected to ublox sensor {self.name} @ {38400}")
                self.reader = ubx.UBXReader(self.conn, protfilter=2)

        self.timing_results = ""
        self.identities = ""

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

        msg_count = 0
        ack_count = 0

        if self.__new_baudrate:
            self.conn = serial.Serial(self.__port, self.__brate, timeout=1)
            #self.conn = serial.Serial(self.__port, 38400, timeout=1)
            if self.conn.is_open:
                logging.info(f"Connected to ublox sensor {self.name} @ {self.__brate}")
                #logging.info(f"Connected to ublox sensor {self.name} @ {38400}")
                self.reader = ubx.UBXReader(self.conn, protfilter=2)

        for i in range(2):
            
            count = 0
            t0 = time.perf_counter()

            print('Enter loop')
            self.conn.write(serial_cfgs)
            msg_count += 1
            logging.info(
                f"Sent UBLOX configuration message {cfgs} - Count: {msg_count}"
            )
            tm = time.perf_counter()
            tf = time.perf_counter()
            while tf- tm < 1:
                self.read()
                tf = time.perf_counter()
                
            logging.info(f"Elapsed time reading GPS: {tf - tm}")
            
            
            _, parsed_data = self.read()
            
            if parsed_data.identity == "ACK-ACK":
                ack_count += 1

            while parsed_data.identity != "ACK-ACK":
                _, parsed_data = self.read()
                logging.info(f"Count: {count} - {parsed_data.identity}")
                if parsed_data.identity == "ACK-ACK":
                    ack_count += 1

                if count > 20:
                    break
                count += 1
            tf = time.perf_counter()
            while tf- tm < 1:
                self.read()
                tf = time.perf_counter()
                
            logging.info(f"Elapsed time waiting for ACK: {tf - tm}")

        if ack_count == 2:
            logging.info("UBlox Sensor Configured Correctly")

        if self.__new_baudrate:
            t0 = time.perf_counter()
            msg_baud = ubx.UBXMessage.config_set(
                1, 0, [("CFG_UART1_BAUDRATE", self.__brate)]
            )
            self.conn.write(msg_baud.serialize())
            t0 = time.perf_counter()
            while time.perf_counter() - t0 <= 1.0:
                pass

            del self.reader
            self.conn.close()
            t0 = time.perf_counter()
            while time.perf_counter() - t0 <= 0.5:
                pass

            self.conn = serial.Serial(self.__port, self.__brate, timeout=1)

            if self.conn.is_open:
                logging.info(f"Connected to ublox sensor {self.name} @ {self.__brate}")

                self.reader = ubx.UBXReader(self.conn)

    def read_continous_binary(self, shutdown_flag, datafile_name):

        loop_start = time.time()
        t_prev = loop_start

        #while not flag.is_set():
            #sensor_lock.acquire()
            #msg = self.read()
            #sensor_lock.release()
            #fs.write(msg)
        try:
            datafile = open(datafile_name, "r+b")
        except FileNotFoundError:
            datafile = open(datafile_name, "x+b")

        while not shutdown_flag.is_set():
            t_start = time.perf_counter_ns()
            msg, parsed = self.read()
            t_end = time.perf_counter_ns()

            read_time = t_end - t_start
            t = time.time()

            # Push the data to the queue
            datafile.write(msg)
            
            print_time = datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S.%f")
            #logging.info(f"Timestamp: {print_time}, Read Time: {read_time}, Data Type: {parsed.identity}")

            self.timing_results += f"{print_time} {read_time / 1e6} {(t - t_prev) * 1e3} \n"
            self.identities += f"{parsed.identity} \n"

            t_prev = t
            current_time = time.time()
            if current_time - loop_start >= 1800:
                print("GPS Loop Done")
                with open(f"porter/sensors/testing/gps_timing{self.file_name}.txt", 'w') as f:
                    f.write(self.timing_results)
                with open(f"porter/sensors/testing/gps_identities{self.file_name}.txt", 'w') as f2:
                    f2.write(self.identities)
                break;
            
        self.close()

    def read(self):

        return self.reader.read()

    def close(self):

        self.conn.close()

        logging.info(f"Closed ublox sensor {self.name}")
