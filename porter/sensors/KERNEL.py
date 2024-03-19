import serial
import pickle
import copy

import porter.sensors.sensors_db.KERNEL as Kdb
import porter.sensors.KERNEL_utils as utils

import logging

logger = logging.getLogger()


class KernelInertial:

    def __init__(self, port, baudrate, **kwargs):

        self.port = port
        self.baudrate = baudrate

        self.__first_msg = True

        self.conn = serial.Serial(port, baudrate=baudrate, timeout=1)

        name = kwargs.get("name", "Generic Kernel")

        if self.conn.is_open:
            logger.info(f"Connected to KERNEL sensor {name}")

    def _check_rate(self, mode):

        length = Kdb.MODES[mode]["length"] + 8
        bits_per_sample = 11

        rate_max = self.baudrate / bits_per_sample / length

        rate_max = int(5 * round(rate_max / 5))

        return rate_max

    def payload_cmds(self, mode):

        msg = (
            utils.HEADER
            + b"\x00"
            + b"\x00"
            + b"\x07"
            + b"\x00"
            + Kdb.MODES[mode]["Address"]
        )

        chk = utils._checksum(msg)

        return msg + chk, chk

    def payload_UDD(self, data):

        if isinstance(data, bytes):
            return data

        elif isinstance(data, list):
            msg = b""

            for i in data:
                if isinstance(i, str):
                    msg += Kdb.User_Defined_Data[i]["Address"]

            return msg

    def configure(self, config):

        mode = config["mode"]

        self._INC_mode = mode

        if mode == "USER_DEFINED_DATA":
            msg_1, chk = self.payload_cmds(mode)
            msg_2 = self.payload_UDD(config["UDD_data"])

            self.conn.write(msg_1)
            self.conn.write(msg_2)
        else:
            msg, chk = self.payload_cmds(mode)

            self.conn.write(msg)

        ack = self.conn.read_until(expected=utils.HEADER)[:-2]

        val = copy.copy(ack[5:7])

        if val == chk:
            logger.info("Sent message to start collecting Inclinometer data")
            logger.info(f"Mode Used: {mode}")
        else:
            logger.info("Cannot connect to inclinometer")

    def read(self, chunk_size=None):

        if self.__first_msg:
            msg = self._find_msg()
        else:
            if chunk_size is None:
                msg = self.conn.read(self.expected_length)
            else:
                msg = self.conn.read(chunk_size)

        return msg

    def close(self):

        self.conn.close()

        logging.info(f"Closed sensor {self.name}")

    def _find_msg(self):
        """Find the first message available with output data"""

        temp = self.conn.read_until(expected=utils.HEADER)[:-2]
        pre = self.conn.read(4)

        length = int.from_bytes(pre[2:3], byteorder="little", signed=False)

        if self.__first_msg:
            self.expected_length = copy.copy(length)
            self.__first_msg = False

        payload = self.conn.read(length - 4)

        if len(payload) > len(temp) - 4:
            msg = pre + payload
        else:
            msg = temp

        return msg, length

    def read_single(self, decode=False, return_dict=False):
        """Read the first single message available from a Kernel Device"""

        msg, _ = self._find_msg()

        if decode:
            msg_class = utils.KernelMsg()
            msg = msg_class.decode_single(msg, return_dict=return_dict)

        return msg

    def _save_binary(self, chunks_size=50, max_bytes=None, filename="INC_Data"):

        count = 0

        pck = open(filename + "_" + self._INC_mode, "ab")

        while True:

            pickle.dump(self.conn.read(chunks_size), pck)

            if max_bytes is not None:
                if count > int(max_bytes / chunks_size):
                    break
            count += 1

        logger.info("Stop Collecting Data")

    def stream_data(self, max_counter=None):

        msg_class = utils.KernelMsg()

        first_msg, length = self._find_msg()

        msg = msg_class.decode_single(first_msg, return_dict=True)

        print(msg.keys())
        print(list(msg.values()))

        counter = 0

        while True:
            temp = self.conn.read(length)
            print(msg_class.decode_single(temp))
            if counter > max_counter:
                break
            counter += 1
