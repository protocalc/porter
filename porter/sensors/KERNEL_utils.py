import struct
import pickle

import porter.sensors.sensors_db.KERNEL as Kdb

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
        modes = list(Kdb.MODES.keys())

        print('msg_type', msg_type)

        idx = self.msg_address.index(msg_type)

        struct_type = '<'+''.join(Kdb.MODES[modes[idx]]['Type'])
        scale = Kdb.MODES[modes[idx]]['Scale']

        vals = struct.unpack(struct_type, msg[type_idx+3:-2])

        if return_dict:
            vals = dict(zip(
                Kdb.MODES[modes[idx]]['Parameters'],
                list( map( lambda x,y: x/y, vals, scale ) )
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
