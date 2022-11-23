import serial
import struct
import pickle
import sensors.sensors_db.KERNEL as Kdb
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

HEADER = b'\xAA\x55'

def _checksum(msg):
    """Compute the checksum of a message
    
    The checksum is the arithmetical sum of all the bytes in the message
    excluding the header. The resulting sum is an unsigned short integer
    whose Least Significant Byte is first

    Args:
        msg (bytes): message used to compute the checksum

    Return:
        checksum (bytes)

    """

    if msg.startswith(HEADER):
        msg = msg[2:]

    return sum(msg).to_bytes(2, byteorder='little', signed=False)


class KernelMsg:

    def __init__(self):

        self.msg_address = []

        for i in Kdb.MODES.keys():
            self.msg_address.append(Kdb.MODES[i]['Address'])


    def decode_single(self, msg, return_dict=False):
        """Decode a single message sent by the inclinometer

        The structure of the message is presented in the KERNEL IMU ICD v1.21

        Args:
            msg (bytes): message to be decoded
        Return:
            vals ()
        """

        if msg[:2] == HEADER:
            type_idx = 3
        else:
            type_idx = 1

        msg_type = msg[type_idx].to_bytes(1, byteorder='little')
        modes = Kdb.MODES.keys()

        idx = self.msg_address.index(msg_type)

        struct_type = '<'+''.join(Kdb.MODES[modes[idx]]['Type'])
        scale = Kdb.MODES[modes[idx]]['Scale']

        vals = struct.unpack(struct_type, msg[type_idx+3:-2])

        if return_dict:
            vals = dict(zip(
                Kdb.MODES[modes[idx]]['Parameters'],
                list( map( lambda x,y: x*y, vals, scale ) )
                ))

        return vals

    def decode_multi(self, filename):

        """Decode multiple messages saved in a binary file
        """

        count = 0
        
        with open(filename, 'rb') as pck:
            data = pickle.load(pck)

        data = data.partition(HEADER)

        for i in data:
            if i == HEADER:
                pass
            
            else:
                if count == 0:
                    if len(data[count]) < len(data[count+2]):
                        pass
                    else:
                        vals = self.decode_single(i, return_dict=True)
                        keys = vals.keys()
                else:
                    if vals in locals():
                        temp = self.decode_single(i)
                        for i in range(len(keys)):
                            vals[keys[i]] = temp[i]
                    else:
                        vals = self.decode_single(i, return_dict=True)
                        keys = vals.keys()

        return vals

class KernelInertial:

    def __init__(self, port, baudrate, **kwargs):

        self.port = port
        self.baudrate = baudrate

        self.conn = serial.Serial(port, baudrate=baudrate, timeout=1)

        name = kwargs.get('name', 'Generic Kernel')

        if self.conn.is_open:
            logging.info(f'Connected to KERNEL sensor {name}')
       
    def _check_rate(self, mode):

        length = Kdb.MODES[mode]['length'] + 8
        bits_per_sample = 11

        rate_max = (
            self.baudrate
            / bits_per_sample
            / length
            )

        rate_max = int(5 * round(rate_max/5))

        return rate_max

    def payload_cmds(self, mode):

        msg = (
            HEADER
            + b'\x00'
            + b'\x00'
            + b'\x07'
            + b'\x00'
            + Kdb.MODES[mode]['Address']
            )

        chk = _checksum(msg)

        return msg + chk

    def payload_UDD(self, data):

        if isinstance(data, bytes):
            return data
        
        elif isinstance(data, list):
            msg = b''

            for i in data:
                if isinstance(i, str):
                    msg += Kdb.User_Defined_Data[i]['Address']
            
            return msg

    def configure(self, config):

        mode = config['mode']

        self._INC_mode = mode

        if mode == 'USER_DEFINED_DATA':
            msg_1 = self.payload_cmds(mode)
            msg_2 = self.payload_UDD(config['UDD_data'])

            self.conn.write(msg_1)
            self.conn.write(msg_2)
        else:
            self.conn.write(self.payload_cmds(mode))

        logging.info('Sent message to start collecting Inclinometer data')
        logging.info(f'Mode Used: {mode}')

    def _find_msg(self):

        """Find the first message available with output data
        
        """

        temp = self.conn.read_until(expected=HEADER)[:-2]
        pre = self.conn.read(4)

        length = int.from_bytes(pre[2], byteorder='little', signed=False)

        payload = self.read(length-4)

        if len(payload) > len(temp)-4:
            msg = pre + payload
        else:
            msg = temp

        return msg, length

    def read_single(self, decode=False):

        """ Read the first single message available from a Kernel Device
        
        """

        msg, _ = self._find_msg()

        if decode:
            msg_class = KernelMsg()
            msg = msg_class.decode_single(msg)
        
        return msg
    
    def _save_binary(self, chunks_size=50, max_bytes=None, filename='INC_Data'):

        count = 0

        pck = open(filename+'_'+self._INC_mode, 'ab')

        while True:

            pickle.dump(self.conn.read(chunks_size), pck)
            
            if max_bytes is not None:
                if count > int(max_bytes/chunks_size):
                    break
            count += 1

        logging.info('Stop Collecting Data')
    
    def stream_data(self, max_counter=None):

        msg_class = KernelMsg()
        
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

        


        


    
