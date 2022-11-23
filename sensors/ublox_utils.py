import struct
from bitarray import util, bitarray
import numpy as np

import sensors.sensors_db.ublox as ubx_db


HEADER = bytes((0xB5, 0x62))
RTCM_HEADER = b'\xd3'

### Messages categories availables and their endlines
ENDLINES = ['$', HEADER]
MSG_CAT = ['NMEA', 'UBX']

class Field:

    def __init__(self, name, fmt, aux, struct_obj=None):

        """ Class for decoding and encoding a field in a UBX message
        Args:
            name (str): a string with the name of the field to be
                decoded or encoded
            fmt (str): a string with the format of the field to be
                decoded or encoded. The string needs to be accepted
                by the struct package
            aux (str): an auxiliary list that contains information about the
                unit of the field and the scale factor. If both are
                absent than the value is None
            struct_obj: a struct object that contains already the information
                regarding the format of the field
        """

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

        """
        Decode a single field.
        Parameters:
        - msg: the field to be decoded
        - ack: if True the field to be decoded is part of an
               acknowledgment message
        - cls_ack: used only if ack=True, it is the address '
                   of the ACK class
        - rep_count: counter used in case of group repetition to
                     rename the field
        """

        if ack:
            if self.name == 'clsID':
                for i in ubx_db.ubx_dict.keys():
                    if ubx_db.ubx_dict[i]['char'] == msg:
                        val = i
                        break
            elif self.name == 'msgID':
                for i in ubx_db.ubx_dict[cls_ack].keys():
                    if i == 'char':
                        pass
                    else:
                        if ubx_db.ubx_dict[cls_ack][i]['char'] == msg:
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

    """
    Class for decoding and encoding a bitfield in a UBX message
    """

    def __init__(self, name, fmt, subfields, aux, struct_obj=None):

        """
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
        """

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

        """
        Required argoments for the class:
        - elements: A template with all the elements that are parts of the group.
                   This is formatted similarly to the payload key of
                   a CLASS_ID element of the ubx_db.py file. For a full format template
                   check the "group" key in the payload. This element needs
                   to have information about the format of each value
        - aux: An auxiliary template that is formatted as the "group"
               aux key of a CLASS_ID element of the ubx_db.py file. This element needs
               to have information about the unit and the scaling factor
               of the value
        """

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

        """
        Compute the length of each repetition in the group
        """

        self.reps_length = 0

        for i in self.fields_key:

            if isinstance(self.elements[i], tuple):
                self.reps_length += (struct.Struct('<'+self.elements[i][0])).size
            else:
                self.reps_length += (struct.Struct('<'+self.elements[i])).size


    def decode_single(self, msg, rep_count=None):

        """
        Decode a single repetition of the group
        Parameters:
        - msg: the message to be decoded
        - rep_count: the index number of the single repetition
        """

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

        """
        Decode the entire group. It calls recursively the
        decode_single method
        Parameters:
        - msg: the group part of the payload to be decoded
        """

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
                        key_id = ubx_db.UBX_CONFIG_DATABASE[val[i][0]][0]
                        val_fmt = ubx_db.UBX_CONFIG_DATABASE[val[i][0]][1]
                    else:
                        key_id = val[i][0]

                        for i in ubx_db.UBX_CONFIG_DATABASE.keys():
                            if ubx_db.UBX_CONFIG_DATABASE[i][0] == key_id:
                                val_fmt = ubx_db.UBX_CONFIG_DATABASE[i][1]
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

    """
    Class to encode or decode a UBX Message Payload
    """

    def __init__(self, payload, aux):

        """
        Required argoments for the class:
        - payload: A payload template that is formatted as the payload key of
                   a CLASS_ID element of the ubx_db.py file. This element needs
                   to have information about the format of each value
        - aux: An auxiliary template that is formatted as the aux key of
               a CLASS_ID element of the ubx_db.py file. This element needs
               to have information about the unit and the scaling factor
               of the value
        """

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

    """
    Class for decoding and encoding a UBX message
    """

    def __init__(self, **kwargs):

        """
        Possible argoments of the class
        - msg: the ubx message to be decoded
        - msg_class: the class of the message to be encoded
        - msg_id: the id of the message to be encoded
        - values: the values associated with the class and id to be encoded
        """

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

        return ubx_db.ubx_dict[class_key][id_key]['name']

    def decode(self, msg, validate=True):

        class_msg = msg[2:3]
        msg_id = msg[3:4]

        for i in ubx_db.ubx_dict.keys():
            if ubx_db.ubx_dict[i]['char'] == class_msg:
                self.msg_class = i
                break
        for i in ubx_db.ubx_dict[self.msg_class].keys():
            if i == 'char':
                pass
            else:
                if ubx_db.ubx_dict[self.msg_class][i]['char'] == msg_id:
                    self.msg_id = i
                    break

        self.name = self.get_name(self.msg_class, self.msg_id)

        if self.msg_class == 'ESF' and self.msg_id == 'MEAS':
            payload_template, aux_template = self.esfmeas(msg)

            payload = Payload(payload_template, aux_template)

        else:
            payload = Payload(ubx_db.ubx_dict[self.msg_class][self.msg_id]['payload'],
                              ubx_db.ubx_dict[self.msg_class][self.msg_id]['aux'])

        
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
            return ubx_db.ubx_dict[self.msg_class][self.msg_id]['payload'], \
                ubx_db.ubx_dict[self.msg_class][self.msg_id]['aux']
        else:
            payload_copy = ubx_db.ubx_dict[self.msg_class][self.msg_id]['payload'].deepcopy()
            aux_copy = ubx_db.ubx_dict[self.msg_class][self.msg_id]['aux'].deepcopy()

            payload_copy.pop('calibTtag')
            aux_copy.pop('calibTtag')
            
            return payload_copy, aux_copy
        
    def encode(self, vals, msgclass=None, msgid=None):

        if msgclass is not None:
            self.msg_class = msgclass
        if msgid is not None:
            self.msg_id = msgid
        
        payload = Payload(ubx_db.ubx_dict[self.msg_class][self.msg_id]['payload'],
                          ubx_db.ubx_dict[self.msg_class][self.msg_id]['aux'])

        msg_payload = payload.encode(vals)
        
        length = len(msg_payload)

        msg_payload = (
            ubx_db.ubx_dict[self.msg_class]['char']
            + ubx_db.ubx_dict[self.msg_class][self.msg_id]['char']
            + struct.pack('<H', length)
            + msg_payload
            )

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
