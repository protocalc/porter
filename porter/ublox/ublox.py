import struct
import ublox.ubx as ubx
import ublox.ubx_cfg_db as ubx_cfg_db
import pickle
from bitarray import util, bitarray
import serial
import h5py
import numpy as np

HEADER = bytes((0xB5, 0x62))
RTCM_HEADER = b'\xd3'

### Messages categories availables and their endlines
ENDLINES = ['$', HEADER]
MSG_CAT = ['NMEA', 'UBX']

class Field:

    '''
    Class for decoding and encoding a field in a UBX message
    '''

    def __init__(self, name, fmt, aux, struct_obj=None):

        '''
        Parameters:
        - name: str, a string with the name of the field to be 
                decoded or encoded
        - fmt: str, a string with the format of the field to be 
               decoded or encoded. The string needs to be accepted
               by the struct package
        - aux: an auxiliary list that contains information about the 
               unit of the field and the scale factor. If both are 
               absent than the value is None
        - struct_obj: a struct object that contains already the information
                      regarding the format of the field
        '''

        self.name = name
        self.fmt = fmt
        if isinstance(aux, list):
            self.scale = aux[0]
            self.unit = aux[1]
        else:
            self.unit = None
            self.scale = 1

        if struct_obj is None:
            self.b = struct.Struct('<'+self.fmt)
        else:
            self.b = struct_obj

    def decode(self, msg, ack, cls_ack=None, rep_count=None):

        '''
        Decode a single field.
        Parameters:
        - msg: the field to be decoded
        - ack: if True the field to be decoded is part of an 
               acknowledgment message
        - cls_ack: used only if ack=True, it is the address 
                   of the ACK class
        - rep_count: counter used in case of group repetition to 
                     rename the field 
        '''

        if ack:
            if self.name == 'clsID':
                for i in ubx.ubx_dict.keys():
                    if ubx.ubx_dict[i]['char'] == msg:
                        val = i
                        break
            elif self.name == 'msgID':
                for i in ubx.ubx_dict[cls_ack].keys():
                    if i == 'char':
                        pass
                    else:
                        if ubx.ubx_dict[cls_ack][i]['char'] == msg:
                            val = i
                            break
        else:                
            val = self.b.unpack(msg)[0]

        if isinstance(val, float) or isinstance(val, int):
            val *= self.scale

        if self.name == 'sTtag':
            if rep_count is not None:
                self.name = self.name + '_' +str(int(rep_count))

        if self.unit is not None:
            return [self.name+' ('+self.unit+')'], [val], len(msg)
        else:
            return [self.name], [val], len(msg)

    def encode(self, val):

        return struct.pack('<'+self.fmt, val)

class BitField:

    '''
    Class for decoding and encoding a bitfield in a UBX message
    '''

    def __init__(self, name, fmt, subfields, aux, struct_obj=None):

        '''
        Parameters:
        - name: str, a string with the name of the bitfield to be 
                decoded or encoded
        - fmt: str, a string with the format of the bitfield to be 
               decoded or encoded. The string needs to be accepted
               by the struct package
        - subfields: a dictionary containing the subfields name and 
                     starting and ending bit. 
        - struct_obj: a struct object that contains already the information
                      regarding the format of the field
        '''

        self.name = name
        self.fmt = fmt
        self.subfields = subfields

        self.template = False

        if isinstance(aux, type(None)):
            pass
        elif isinstance(aux, list):
            self.scale = aux[:,0]
            self.unit = aux[:,1]
        else:
            self.aux = aux
            self.template = True

        if struct_obj is None:
            self.b = struct.Struct('<'+self.fmt)
        else:
            self.b = struct_obj

    def decode(self, msg, add_str=None):

        msg_size = len(msg)

        bfield = bitarray(endian='little')
        bfield.frombytes(msg)

        values = []
        fields_name = []
        count = 0

        for i in self.subfields.keys():

            start = self.subfields[i]['start']
            end = self.subfields[i]['start']+self.subfields[i]['length']
            temp = bfield[start:end]

            if self.subfields[i]['type'] == 'unsigned':
                signed = False
            else:
                signed = True

            val = util.ba2int(temp, signed=signed)

            if self.template:
                if i == self.aux['ref_key']:
                    param_dict = self.aux[str(int(val))]
                else:
                    values.append(val)
            
            else:
                try:
                    values.append(val*self.scale[count])
                
                    if add_str is not None:
                        fields_name.append(str(i)+'_'+add_str+' ('+self.unit[count]+')')
                    else:
                        fields_name.append(str(i)+' ('+self.unit[count]+')')
                
                except AttributeError:
                    values.append(val)
                
                    if add_str is not None:
                        fields_name.append(str(i)+'_'+add_str)
                    else:
                        fields_name.append(str(i))
                
                count +=1

        if self.template:
            values[0] *= param_dict['scale']
            fields_name.append(param_dict['name']+' ('+param_dict['unit']+')')

        return fields_name, values, msg_size

    def encode(self, vals):
        ba = bitarray(len(self.b), endian='little')

        for i in self.subfields.keys():
            
            if self.subfields[i]['type'] == 'unsigned':
                signed = False
            else:
                signed = True

            temp = util.int2ba(vals[i], signed=signed)

            start = self.subfields[i]['start']
            end = self.subfields[i]['start']+self.subfields[i]['length']+1

            ba[start:end] = temp

        return ba.tobytes()

class Group:

    def __init__(self, elements, aux, **kwargs):

        '''
        Required argoments for the class:
        - elements: A template with all the elements that are parts of the group.
                   This is formatted similarly to the payload key of 
                   a CLASS_ID element of the ubx.py file. For a full format template
                   check the "group" key in the payload. This element needs 
                   to have information about the format of each value
        - aux: An auxiliary template that is formatted as the "group" 
               aux key of a CLASS_ID element of the ubx.py file. This element needs 
               to have information about the unit and the scaling factor 
               of the value
        '''

        self.elements = elements
        self.aux = aux
        self.fields_key = elements.keys() # fields of the group

        self.compute_reps_length() 

        self.reps = kwargs.get('reps', None)

        if self.reps is None:
            self.group_length = kwargs.get('group_length', None)
            
            if self.group_length is not None:
                self.reps = self.group_length/self.reps_length

        if self.reps is None and self.group_length is None:
            print('ERROR')

    def compute_reps_length(self):

        '''
        Compute the length of each repetition in the group
        '''

        self.reps_length = 0

        for i in self.fields_key:

            if isinstance(self.elements[i], tuple):
                self.reps_length += (struct.Struct('<'+self.elements[i][0])).size
            else:
                self.reps_length += (struct.Struct('<'+self.elements[i])).size


    def decode_single(self, msg, rep_count=None):

        '''
        Decode a single repetition of the group 
        Parameters:
        - msg: the message to be decoded
        - rep_count: the index number of the single repetition
        '''

        offset = 0

        values = []
        fields_name = []

        for i in self.fields_key:

            if isinstance(self.elements[i], tuple):
                b = struct.Struct('<'+self.elements[i][0])

                bf = BitField(i, self.elements[i][0], self.elements[i][1], self.aux[i], b)
                res = bf.decode(msg[offset:offset+b.size], rep_count)
            
            else:
                b = struct.Struct('<'+self.elements[i])
                f = Field(str(i), self.elements[i], self.aux[i], b)

                res = f.decode(msg[offset:offset+b.size], ack=False, rep_count=rep_count)

            fields_name = fields_name + res[0]
            values = values + res[1]
            offset += res[2]

        return fields_name, values

    def decode(self, msg):

        '''
        Decode the entire group. It calls recursively the 
        decode_single method
        Parameters:
        - msg: the group part of the payload to be decoded
        '''

        offset = 0

        values = []
        fields_name = []

        for i in range(int(self.reps)):
            
            idx_start = self.reps_length*i
            idx_end = (i+1)*self.reps_length

            fields_single, values_single = self.decode_single(msg[idx_start:idx_end], \
                                                              rep_count=str(int(i)))

            fields_name = fields_name + fields_single
            values = values + values_single

            offset += self.reps_length

        return fields_name, values, offset

    def encode_single(self, val):

        msg = b''

        for i in self.fields_key:

            if isinstance(val[i], tuple):

                if isinstance(val[i][1], dict):
                    b = struct.Struct('<'+self.elements[i][0])

                    bf = BitField(i, self.elements[i][0], self.elements[i][1], self.aux[i], b)
                    msg += bf.encode(val)
                else:
                    ### This case takes care of the configuration group that are expressed as tuple
                    if isinstance(val[i][0], str):
                        key_id = ubx_cfg_db.UBX_CONFIG_DATABASE[val[i][0]][0]
                        val_fmt = ubx_cfg_db.UBX_CONFIG_DATABASE[val[i][0]][1]
                    else:
                        key_id = val[i][0]

                        for i in ubx_cfg_db.UBX_CONFIG_DATABASE.keys():
                            if ubx_cfg_db.UBX_CONFIG_DATABASE[i][0] == key_id:
                                val_fmt = ubx_cfg_db.UBX_CONFIG_DATABASE[i][1]
                                break
                    msg += struct.pack('<L', key_id)

                    msg += struct.pack('<'+val_fmt, val[i][1])

            else:
                b = struct.Struct('<'+self.elements[i])
                f = Field(str(i), self.elements[i], self.aux[i], b)
                
                msg += f.encode(val)
        
        return msg

    def encode(self, vals):

        msg = b''

        keys = vals.keys()

        for i in range(self.reps):

            temp_vals = [vals[key][i] for key in keys]
            
            msg += self.encode_single(dict(zip(list(keys), temp_vals)))

        return msg

class Payload:

    '''
    Class to encode or decode a UBX Message Payload
    '''

    def __init__(self, payload, aux):

        '''
        Required argoments for the class:
        - payload: A payload template that is formatted as the payload key of 
                   a CLASS_ID element of the ubx.py file. This element needs 
                   to have information about the format of each value
        - aux: An auxiliary template that is formatted as the aux key of 
               a CLASS_ID element of the ubx.py file. This element needs 
               to have information about the unit and the scaling factor 
               of the value
        '''

        self.payload = payload
        self.aux = aux
        self.payload_fields = payload.keys()

        ### Info for estimating the length of the payload

        self.reps_string = False

        if 'group' in self.payload_fields:

            if self.payload['group'][0] is not None:
                
                if isinstance(self.payload['group'][0], int):
                    self.reps = self.payload['group'][0]
                
                elif isinstance(self.payload['group'][0], str):
                    self.reps_string = True
                    self.reps_string_value = self.payload['group'][0]

            else:
                self.length_no_group = 0
                for i in self.payload_fields:
                    if i == 'group':
                        pass
                    else:
                        if isinstance(self.payload[i], tuple):
                            fmt = self.payload[i][0]
                        else:
                            fmt = self.payload[i]

                        self.length_no_group += struct.Struct('<'+fmt).size
                    
    def decode(self, msg, ack=False):

        offset = 0
        values = []
        fields_name = []

        cls_ack = None

        for i in self.payload_fields:
            
            if isinstance(self.payload[i], tuple):
                
                if i == 'group':

                    if self.length_no_group == 0:
                        g = Group(self.payload[i][1], self.aux[i], reps=self.reps)
                        g.compute_reps_length()
                        group_length = self.reps*g.reps_length

                    else:
                        group_length = len(msg)-self.length_no_group
                  
                        g = Group(self.payload[i][1], self.aux[i], group_length=group_length)

                    res = g.decode(msg[offset:offset+group_length])

                else:
                    b = struct.Struct('<'+self.payload[i][0])

                    bf = BitField(i, self.payload[i][0], self.payload[i][1], b, self.aux[i])
                    res = bf.decode(msg[offset:offset+b.size])

                    if self.reps_string:
                        if self.reps_string_value in res[0]:
                            idx, = np.where(res[0] == self.reps_string_value)
                            self.reps = int(res[1][idx])
 
            else:
                b = struct.Struct('<'+self.payload[i])
                f = Field(str(i), self.payload[i], self.aux[i], b)

                res = f.decode(msg[offset:offset+b.size], ack, cls_ack)

                if ack:

                    if res[0][0] == 'clsID':
                        cls_ack=res[1][0]

                if self.reps_string:
                    if self.reps_string_value == str(i):
                        self.reps = int(res[1])

            fields_name = fields_name + res[0]
            values = values + res[1]

            offset += res[2]

        return fields_name, values

    def encode(self, vals):
            
        count = 0
        msg = b''
    
        for i in self.payload_fields:
            if isinstance(self.payload[i], tuple):

                if i == 'group':
                    reps = len(vals['group'][list(vals['group'].keys())[0]])
                    g = Group(self.payload[i][1], self.aux[i], reps=reps)

                    msg += g.encode(vals[i])

                else:
                    b = struct.Struct('<'+self.payload[i][0])

                    bf = BitField(i, self.payload[i][0], self.payload[i][1], b, self.aux[i])
                    msg += bf.encode(vals[i])
                
            else:

                b = struct.Struct('<'+self.payload[i])
                f = Field(str(i), self.payload[i], b, self.aux[i])

                msg += f.encode(vals[i])

            count += 1

        return msg

class UBXMessage:

    '''
    Class for decoding and encoding a UBX message 
    '''

    def __init__(self, **kwargs):

        '''
        Possible argoments of the class
        - msg: the ubx message to be decoded
        - msg_class: the class of the message to be encoded
        - msg_id: the id of the message to be encoded 
        - values: the values associated with the class and id to be encoded
        '''

        msg = kwargs.get('msg', None)

        if msg is not None:
            if isinstance(msg, bytes):
                self.decode(msg)

        self.msg_class = kwargs.get('msg_class', None)
        self.msg_id = kwargs.get('msg_id', None)
        self.values = kwargs.get('values', None)

        if self.msg_class is not None and self.msg_id is not None and \
           self.values is not None:

            self.encode(self.values)

    def get_name(self, class_key, id_key):

        return ubx.ubx_dict[class_key][id_key]['name']

    def decode(self, msg, validate=True):

        class_msg = msg[2:3]
        msg_id = msg[3:4]

        for i in ubx.ubx_dict.keys():
            if ubx.ubx_dict[i]['char'] == class_msg:
                self.msg_class = i
                break
        for i in ubx.ubx_dict[self.msg_class].keys():
            if i == 'char':
                pass
            else:
                if ubx.ubx_dict[self.msg_class][i]['char'] == msg_id:
                    self.msg_id = i
                    break

        self.name = self.get_name(self.msg_class, self.msg_id)

        if self.msg_class == 'ESF' and self.msg_id == 'MEAS':
            payload_template, aux_template = self.esfmeas(msg)

            payload = Payload(payload_template, aux_template)

        else:
            payload = Payload(ubx.ubx_dict[self.msg_class][self.msg_id]['payload'],
                              ubx.ubx_dict[self.msg_class][self.msg_id]['aux'])

        
        if self.msg_class == 'ACK':
            ack = True
        else:
            ack = False            
            
        self.fields_name, self.values = payload.decode(msg[6:-2], ack)

        if validate:
            check = self.checksum(msg[2:-2])
            if check[0] != msg[-2] or check[1] != msg[-1]:
                print('Error')
        
    def esfmeas(self, msg):
        
        flags = bitarray(endian='little')
        flags.frombytes(msg[8:10])

        if util.ba2int(flags[3:4], signed='unsigned') == 1:
            return ubx.ubx_dict[self.msg_class][self.msg_id]['payload'], \
                ubx.ubx_dict[self.msg_class][self.msg_id]['aux']
        else:
            payload_copy = ubx.ubx_dict[self.msg_class][self.msg_id]['payload'].deepcopy()
            aux_copy = ubx.ubx_dict[self.msg_class][self.msg_id]['aux'].deepcopy()

            payload_copy.pop('calibTtag')
            aux_copy.pop('calibTtag')
            
            return payload_copy, aux_copy
        
    def encode(self, vals, msgclass=None, msgid=None):

        if msgclass is not None:
            self.msg_class = msgclass
        if msgid is not None:
            self.msg_id = msgid
        
        payload = Payload(ubx.ubx_dict[self.msg_class][self.msg_id]['payload'],
                          ubx.ubx_dict[self.msg_class][self.msg_id]['aux'])

        msg_payload = payload.encode(vals)
        
        length = len(msg_payload)

        msg_payload = ubx.ubx_dict[self.msg_class]['char']+\
            ubx.ubx_dict[self.msg_class][self.msg_id]['char']+\
            struct.pack('<H', length)+\
            msg_payload

        check = self.checksum(msg_payload)

        self.ubx_msg = HEADER+msg_payload+check

    def checksum(self, payload):
        """Return the checksum for the provided payload"""
        check_a = 0
        check_b = 0

        for char in payload:

            check_a += char
            check_a &= 0xFF

            check_b += check_a
            check_b &= 0xFF

        return bytes((check_a, check_b))
       
class UBXio:

    def __init__(self, port=None, baudrate=None, serial_connection=None):

        '''
        Connect to a ublox module using a serial connection. 
        Default baudrate for ublox modules is 38400
        '''

        if serial_connection is None:
            if port is not None and baudrate is not None:
                self.port = port
                self.conn = serial.Serial(self.port, baudrate)
        else:
            self.conn = serial_connection

    def save_binary(self, chunks_size=10, filename='attitude_binary', max_bytes=None):

        '''
        Read continuosly the serial port and then save the data on a pickle file. 
        Data are saved as read, so they are in binary format
        Parameters:
        - chunks_size: int, the number of byte to read each time from the 
                       serial port 
        - filename: str, the name of the pickle file to be create
        - max_bytes: int, the maximum number of bytes to read from the serial port
        '''

        '''
        Add saving NMEA data
        '''

        count = 0

        pck = open(filename, 'ab')
        while True:

            pickle.dump(self.conn.read(chunks_size), pck)
            
            if max_bytes is not None:
                if int(max_bytes/chunks_size) < count:
                    break
            count += 1
    
    def stream(self, stream_len=None, save_data=False, print_data=True, filename='attitude'):

        count = 0

        if save_data:
            f = h5py.File(filename+'.hdf5', 'a')
            try:
                f.create_group('UBX')
            except ValueError:
                pass
            try:
                f.create_group('NMEA')
            except ValueError:
                pass

        msg_cat = self.find_header()

        while True:

            if count == 0:
                msg = self.read(cat=msg_cat)
            else:
                msg = self.read()

            if isinstance(msg, bytes):
                ubxmsg = UBXMessage()
                ubxmsg.decode(msg)
                name, fields, values = ubxmsg.name, \
                    ubxmsg.fields_name, \
                    ubxmsg.values
                
                if save_data:             
                    if name not in list(f['UBX'].keys()):
                        dset = f.create_dataset('UBX/'+name, data=values, shape=(1, len(values)), \
                                                maxshape=(None,len(values)), chunks=(1,len(values)))
                        dset.attrs.create('Fields', np.array(fields, dtype='S'))
                    else:
                        f['UBX/'+name].resize(f['UBX/'+name].shape[0]+1, axis=0)
                        f['UBX/'+name][-1]=values

                if print_data:
                    print(dict(zip(fields, values)))
            else:
                nmea_msg = msg
                if print_data:
                    print(nmea_msg)

            count += 1

            if stream_len is not None:
                if count > stream_len:
                    break

    def find_header(self):

        line = b''

        while True:
            c = self.conn.read(1)

            line += c
            if len(line)>=2:
                if line[-2:] == HEADER:
                    msg_cat = 'ubx'
                    break
                else:
                    if line[-1:] == RTCM_HEADER:
                        msg_cat = 'rtcm'
                        break
                    else:
                        try:
                            if line.decode('utf-8')[-1] == '$':
                                msg_cat = 'nmea'
                                break
                        except UnicodeDecodeError:
                            pass
        return msg_cat

    def read(self, cat=None, first_msg=False):

        if cat is None and first_msg:
            msg_cat = self.conn.read(2)
        else:
            if cat == 'ubx':
                msg_cat = HEADER
            elif cat == 'nmea':
                msg_cat = b'$'
            elif cat == 'rtcm':
                msg_cat = RTCM_HEADER

        if msg_cat == HEADER:

            pre = self.conn.read(4)
            msg_length = struct.unpack('<H', pre[-2:])

            final_msg = self.conn.read(msg_length[0]+2)
            final_msg = msg_cat+pre+final_msg

        else:
            if len(msg_cat) != 1:
                msg_cat_temp = msg_cat[0:1]
            else:
                msg_cat_temp = msg_cat

            if msg_cat_temp == b'$':
                msg = self.conn.read_until(terminator=b'\r\n')

                final_msg = (msg_cat+msg).decode('utf-8')

            elif msg_cat_temp == RTCM_HEADER:
                
                if len(msg_cat) != 1:
                    pre = msg_cat[1:]+self.conn.read(1)
                else:
                    pre = self.conn.read(2)

                msg_length = struct.unpack('!H', pre)

                msg_length = 0x03ff & msg_length[0]

                final_msg = self.conn.read(msg_length+3)

                final_msg = msg_cat[0]+pre+final_msg

        return final_msg

    def class2char(self, msg_class):
        
        if isinstance(msg_class, list):
            class_char = []
            for i in range(len(msg_class)):
                class_char.append(ubx.ubx_dict[msg_class[i]]['char'])
        else:
            class_char = ubx.ubx_dict[msg_class]['char']

        return class_char

    def id2char(self, msg_class, msg_id):
        
        if isinstance(msg_id, list):
            id_char = []
            for i in range(len(msg_id)):
                id_char.append(ubx.ubx_dict[msg_class][msg_id[i]]['char'])
        else:
            id_char = ubx.ubx_dict[msg_class][msg_id]['char']

        return id_char

    def read_msg(self, **kwargs):

        '''
        Read the first message availble from a UBlox device 
        '''

        msg_cat = kwargs.get('msg_cat', None)
        first_msg = kwargs.get('first_msg', True)
        decode = kwargs.get('decode', False)

        if msg_cat is None:
            if first_msg:
                cat = self.find_header()
                if cat == 'ubx':
                    msg_cat = HEADER
                elif cat == 'nmea':
                    msg_cat = b'$'
                elif cat == 'rtcm':
                    msg_cat = RTCM_HEADER
            else:
                msg_cat = self.conn.read(2)
        else:
            if msg_cat == 'ubx':
                msg_cat = HEADER
            elif msg_cat == 'nmea':
                msg_cat = b'$'
            elif msg_cat == 'rtcm':
                msg_cat = RTCM_HEADER

        if msg_cat == HEADER:
            pre = self.conn.read(4)
            msg_length = struct.unpack('<H', pre[-2:])

            final_msg = self.conn.read(msg_length[0]+2)
            final_msg = msg_cat+pre+final_msg

            if decode:
                ubxmsg = UBXMessage()
                ubxmsg.decode(final_msg)
                name, fields, values = ubxmsg.name, \
                    ubxmsg.fields_name, \
                    ubxmsg.values

                return name, fields, values

        else:
            if len(msg_cat) != 1:
                msg_cat_temp = msg_cat[0:1]
            else:
                msg_cat_temp = msg_cat

            if msg_cat_temp == b'$':
                msg = self.conn.read_until(terminator=b'\r\n')

                if decode:
                    final_msg = (msg_cat+msg).decode('utf-8')
                else:
                    final_msg = msg_cat+msg

            elif msg_cat_temp == RTCM_HEADER:
                
                if len(msg_cat) != 1:
                    pre = msg_cat[1:]+self.conn.read(1)
                else:
                    pre = self.conn.read(2)

                msg_length = struct.unpack('!H', pre)
                msg_length = 0x03ff & msg_length[0]

                final_msg = self.conn.read(msg_length+3)
                final_msg = msg_cat[0]+pre+final_msg

        return final_msg

    def read_single_msg(self, **kwargs):

        msg_cat = kwargs.get('msg_cat', None)
        first_msg = kwargs.get('first_msg', True)
        max_bytes = kwargs.get('max_bytes', 10000)

        ubx_class = kwargs.get('ubx_class', None)
        ubx_id = kwargs.get('ubx_id', None)

        nmea_msg = kwargs.get('nmea_msg', None)

        if msg_cat is None:

            if ubx_class is None:
                if nmea_msg is not None:
                    msg_cat = 'nmea'
                else:
                    print('Error')

            else:
                msg_cat = 'ubx'

        if msg_cat == 'ubx':
            if ubx_class is not None:
                if ubx_id is None:
                    ubx_id = list(ubx.ubx_dict[ubx_class].keys())
                    ubx_id = ubx_id[1:]

                    id_char = self.id2char(ubx_class, ubx_id)

                else:
                    if isinstance(ubx_id, str):
                        id_char = ubx.ubx_dict[ubx_class][ubx_id]['char']
                    else:
                        id_char = ubx_id

                class_char = self.class2char(ubx_class)
                vals = self.read_specifc_ubx(class_char, id_char, max_bytes)
            else:
                while True:
                    cat = self.find_header()
                    if cat == 'ubx':
                        pre = self.conn.read(4)
                        msg_length = struct.unpack('<H', pre[-2:])

                        final_msg = self.conn.read(msg_length[0]+2)

                        vals = HEADER+pre+final_msg
                        break

        elif msg_cat == 'rtcm':
            while True:
                if first_msg:
                    cat = self.find_header()
                else:
                    self.conn.read(1)
                    cat = 'rtcm'
                if cat == 'rtcm':
                    pre = self.conn.read(2)
                    msg_length = struct.unpack('!H', pre)
                    msg_length = 0x03ff & msg_length[0]

                    final_msg = self.conn.read(msg_length+3)
                    vals = RTCM_HEADER+pre+final_msg
                    break

        elif msg_cat == 'nmea':
            while True:
                cat = self.find_header()
                if cat == 'nmea':
                    final_msg = self.conn.read_until(terminator=b'\r\n')

                    vals = (b'$'+final_msg).decode('utf-8')
                    break

        return vals
    
    def read_specifc_ubx(self, msg_class, msg_id, max_bytes=None):

        line = b''
        count = 0

        if isinstance(msg_id, list) is False:
            msg_id = list(msg_id)

        while True:
            c = self.conn.read(1)
            line += c

            if line[-2:] == HEADER:
                
                pre = self.conn.read(2)

                if pre[0:1] == msg_class:
                    if pre[1:2] in msg_id:
                        length = self.conn.read(2)

                        payload = self.conn.read(struct.unpack('<H', length)[0])
                        chk = self.conn.read(2)

                        msg = HEADER+pre+length+payload+chk

                        ubxmsg = UBXMessage()
                        ubxmsg.decode(msg)
                        name, fields, values = ubxmsg.name, \
                            ubxmsg.fields_name, \
                            ubxmsg.values

                        print(dict(zip(fields, values)))

                        return name, fields, values

            count += 1
            if max_bytes is not None:
                if count > max_bytes:
                    break
    
    def write_msg(self, msg_class, msg_id, vals, ack=False):

        payload_template = ubx.ubx_dict[msg_class][msg_id]['payload']
        
        if isinstance(vals, dict):
            if len(vals.keys()) != len(payload_template.keys()):
                print('ERROR', payload_template.keys())
                return 0

        ubxmsg = UBXMessage(msg_class=msg_class, msg_id=msg_id)

        ubxmsg.encode(vals)

        self.conn.write(ubxmsg.ubx_msg)

        if ack:
            self.read_single_msg(msg_cat ='ubx', ubx_class='ACK')


class UBXutils:

    def __init__(self, port, baudrate):
        
        self.port = port
        self.baudrate = baudrate

        self.ubx_obj = UBXio(self.port, self.baudrate)

    def change_baudrate(self, baudrate_new, uart_num=1):

        if uart_num == 1:
            uart = 'CFG-UART1-BAUDRATE'
        elif uart_num == 2:
            uart = 'CFG-UART2-BAUDRATE'

        msg_dict = {
            "version": 0,  
            "layers": {
                'ram': 1,
                'bbr': 0,
                'flash': 0
            },
            "transaction": {
                'action': 1,
            },
            "reserved0": 0,
            "group": [(uart, baudrate_new)]
        }

        self.ubx_obj.write_msg('CFG', 'VALSET', msg_dict, True)
        self.ubx_obj.conn.close()

        self.baudrate = baudrate_new

        self.ubx_obj = UBXio(self.port, self.baudrate)

    def enableSurvey(self, survey_time, survey_accuracy):

        '''
        Enable Survey Mode for initializing an RTK base:
        Parameters:
        - survey_time: float. Time for the survey in seconds
        - survey_accuracy: float. Accuracy required for the survey in meters
        '''

        survey_accuracy = int(survey_accuracy*1e4)

        survey_dict = {
            "version": 0,  
            "layers": {
                'ram': 1,
                'bbr': 0,
                'flash': 0
            },
            "transaction": {
                'action': 0,
            }, 
            "reserved0": 0,
            "group": {
                "keys": [('CFG_TMODE_MODE', 1), \
                         ('CFG_TMODE_SVIN_MIN_DUR', int(survey_time)), \
                         ('CFG_TMODE_SVIN_ACC_LIMIT', survey_accuracy)]
            }
        }

        self.ubx_obj.write_msg('CFG', 'VALSET', survey_dict, True) 

    def disableSurvey(self):

        survey_dict = {
            "version": 0,  
            "layers": {
                'ram': 1,
                'bbr': 0,
                'flash': 0
            },
            "transaction": {
                'action': 1,
            },
            "reserved0": 0,
            "group": {
                "keys": [('CFG_TMODE_MODE', 0)]
            }
        }

        self.ubx_obj.write_msg('CFG', 'VALSET', survey_dict, True)

    def confRTCMmsg_output(self, uart_port=2, usb=True):

        '''
        Configure the output of required RTCM messages.
        Optional:
        - uart_port: int. Choose between the UART 1 and 2 as output of 
                     RTCM messages
        '''
        
        if usb:
            rtcm_out = 'CFG_USBOUTPROT_RTCM3X'

            rtcm_msg_1005 = "CFG_MSGOUT_RTCM_3X_TYPE1005_USB"
            rtcm_msg_1074 = "CFG_MSGOUT_RTCM_3X_TYPE1074_USB" 
            rtcm_msg_1084 = "CFG_MSGOUT_RTCM_3X_TYPE1084_USB"
            rtcm_msg_1094 = "CFG_MSGOUT_RTCM_3X_TYPE1094_USB"
            rtcm_msg_1124 = "CFG_MSGOUT_RTCM_3X_TYPE1124_USB"
            rtcm_msg_1230 = "CFG_MSGOUT_RTCM_3X_TYPE1230_USB"
        else:
            if uart_port == 1:
                rtcm_out = 'CFG_UART1OUTPROT_RTCM3X'

                rtcm_msg_1005 = "CFG_MSGOUT_RTCM_3X_TYPE1005_UART1"
                rtcm_msg_1074 = "CFG_MSGOUT_RTCM_3X_TYPE1074_UART1" 
                rtcm_msg_1084 = "CFG_MSGOUT_RTCM_3X_TYPE1084_UART1"
                rtcm_msg_1094 = "CFG_MSGOUT_RTCM_3X_TYPE1094_UART1"
                rtcm_msg_1124 = "CFG_MSGOUT_RTCM_3X_TYPE1124_UART1"
                rtcm_msg_1230 = "CFG_MSGOUT_RTCM_3X_TYPE1230_UART1"

            elif uart_port == 2:
                rtcm_out = 'CFG_UART2OUTPROT_RTCM3X'

                rtcm_msg_1005 = "CFG_MSGOUT_RTCM_3X_TYPE1005_UART2"
                rtcm_msg_1074 = "CFG_MSGOUT_RTCM_3X_TYPE1074_UART2" 
                rtcm_msg_1084 = "CFG_MSGOUT_RTCM_3X_TYPE1084_UART2"
                rtcm_msg_1094 = "CFG_MSGOUT_RTCM_3X_TYPE1094_UART2"
                rtcm_msg_1124 = "CFG_MSGOUT_RTCM_3X_TYPE1124_UART2"
                rtcm_msg_1230 = "CFG_MSGOUT_RTCM_3X_TYPE1230_UART2"


        RTCM_dict = {
            "version": 0,  
            "layers": {
                'ram': 1,
                'bbr': 0,
                'flash': 0
            },
            "transaction": {
                'action': 1,
            },
            "reserved0": 0,
            "group": {
                "keys": [(rtcm_out, 1), \
                         (rtcm_msg_1005, 1), \
                         (rtcm_msg_1074, 1), \
                         (rtcm_msg_1084, 1), \
                         (rtcm_msg_1094, 1), \
                         (rtcm_msg_1124, 1), \
                         (rtcm_msg_1230, 1)]
            }
        }

        self.ubx_obj.write_msg('CFG', 'VALSET', RTCM_dict, True)

    def configure_frequency(self, freq):

        '''
        Set the frequency of the update for the navigation solution
        Parameter:
        - freq: float. Frquency of the update in Hz
        '''

        time = 1/freq*1000.

        update_dict = {
            "version": 0,  
            "layers": {
                'ram': 1,
                'bbr': 0,
                'flash': 0
            },
            "transaction": {
                'action': 1,
            },
            "reserved0": 0,
            "group": {
                "keys": [('CFG_RATE_MEAS', time)]
            }
        }

        self.ubx_obj.write_msg('CFG', 'VALSET', update_dict, True)

    def confRTCMmsg_input(self, uart_port=2):

        '''
        Configure the option to input RTCM messages.
        Optional:
        - uart_port: int. Choose between the UART 1 and 2 as input of 
                     RTCM messages
        '''
        

        if uart_port == 1:
            rtcm_in = 'CFG_UART1INPROT_RTCM3X'

        elif uart_port == 2:
            rtcm_in = 'CFG_UART2INPROT_RTCM3X'


        RTCM_dict = {
            "version": 0,  
            "layers": {
                'ram': 1,
                'bbr': 0,
                'flash': 0
            },
            "transaction": {
                'action': 1,
            },
            "reserved0": 0,
            "group": {
                "keys": [(rtcm_in, 1)]
            }
        }

        self.ubx_obj.write_msg('CFG', 'VALSET', RTCM_dict, True)
             

        
