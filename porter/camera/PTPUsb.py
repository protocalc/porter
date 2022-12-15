import usb
from usb.util import (
    endpoint_type, endpoint_direction, ENDPOINT_TYPE_BULK, ENDPOINT_TYPE_INTR,
    ENDPOINT_OUT, ENDPOINT_IN,
)
import struct
import time
import datetime
import copy
import decimal
import math
import PTPdb
import camerasdb.Sony as sony
from fractions import Fraction

import logging
import os

if logging.getLogger().hasHandlers():
    logger = logging.getLogger()
else:
    path = os.path.dirname(os.path.realpath(__file__))
    date = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    logging.basicConfig(
        filename=path+'/camera_'+date+'.log',
        filemode='w',
        format='%(asctime)s    [%(threadName)s]    %(levelname)s:%(message)s',
        datefmt='%m/%d/%Y %H:%M:%S',
        level=logging.DEBUG
        )

    logger = logging.getLogger('camera')

PTP_USB_CLASS = 0x06

BASE_PTP_MSG_LENGTH = 12

USB_OPERATIONS = {
    'Undefined' : 0x0000,
    'Command': 0x0001,
    'Data' : 0x0002,
    'Response' : 0x0003,
    'Event' : 0x0004
    }

MSG_STRUCT = {
    'Length' : 'L',
    'MsgType' : 'H',
    'OpCode' : 'H',
    'TransactionId' : 'L',
    'Payload' : 'Variable'
}

class find_class(object):
    def __init__(self, class_, name=None):
        self._class = class_
        self._name = name

    def __call__(self, device):
        if device.bDeviceClass == self._class:
            return (
                self._name in usb.util.get_string(device, device.iProduct)
                if self._name else True
            )
        for cfg in device:
            intf = usb.util.find_descriptor(
                cfg,
                bInterfaceClass=self._class
            )
            if intf is not None:
                return (
                    self._name in usb.util.get_string(device, device.iProduct)
                    if self._name else True
                )
        return False

def find_usb_cameras(name=None):
    
    return usb.core.find(
        find_all=True,
        custom_match=find_class(PTP_USB_CLASS, name=name)
    )

def combine_dict(dict1, dict2):

    temp = copy.copy(dict1)

    for key, value in dict2.items():
        if key in dict1:
            temp[key].update(value)
        else:
            temp[key] = value
    
    return temp
            
class PTPusb:

    def __init__(self, camera = None, idVendor = None, idProduct = None, endian = 'little'):

        if isinstance(camera, usb.core.Device):
            self.camera = camera
        else:
            if idProduct and idVendor:
                self.camera = self._choose_specific_camera(
                    idVendor = idVendor,
                    idProduct = idProduct
                    )
            else:
                self.camera = find_usb_cameras()[0]
        
        self.__set_endianess(endian)

        self.transactionId = 0
        self.sessionId = 0
        self.__camera_prop_code = 0

        self._recording_status = False
        self.__video_modes = ['Movie', 'HiFrameRate']
        self.__available_parsers = ['ISO', 'ExposureProgramMode', 'ShutterSpeed']

        self._session_open = False

        self._setup_camera()
        

        usb.util.claim_interface(self.__dev, self.__intf)

        if self.camera.manufacturer == 'Sony':
            import camerasdb.Sony as sony

            self._OPCODES = combine_dict(PTPdb.PTP_OPCODE, sony.SONY_OPCODE)
            self._RESPCODES = combine_dict(PTPdb.PTP_RESPCODE, sony.SONY_RESPCODE)
            self._EVENTCODES = combine_dict(PTPdb.PTP_EVENTCODE, sony.SONY_EVENTCODE)
            self._PROPCODES = combine_dict(PTPdb.PTP_PROPCODE, sony.SONY_PROPCODE)

        else:

            self._OPCODES = copy.copy(PTPdb.PTP_OPCODE)
            self._RESPCODES = copy.copy(PTPdb.PTP_RESPCODE)
            self._EVENTCODES = copy.copy(PTPdb.PTP_EVENTCODE)
            self._PROPCODES = copy.copy(PTPdb.PTP_PROPCODE)

    def __set_endianess(self, value):

        if value.lower() == 'little':
            self.__endian = '<'
        elif value.lower() == 'big':
            self.__endian = '>'
        elif value.lower() == 'native_@':
            self.__endian = '@'
        elif value.lower() == 'native_=':
            self.__endian = '='
        elif value.lower() == 'network':
            self.__endian = '!'

    def _PTPMsg(self, MsgType, MsgOp, params = None):

        '''Method for building messages using PTP protocol
        '''
        
        length = 0

        if params:
            paramsMsg = {
                'DataType': [],
                'Value' : []
            }
            for i in params.keys():
                
                if isinstance(params[i]['DataType'], list):
                    for j in range(len(params[i]['DataType'])):
                        if isinstance(params[i]['Value'][j], bytes):
                            length += len(paramsMsg['Value'])
                        else:
                    
                            length += (
                                struct.Struct(
                                    (
                                        self.__endian
                                        + params[i]['DataType'][j]
                                        )
                                    ).size
                                )

                        paramsMsg['DataType'].append(params[i]['DataType'][j])
                        paramsMsg['Value'].append(params[i]['Value'][j])

                else:
                    paramsMsg['DataType'].append(params[i]['DataType'])
                    paramsMsg['Value'].append(params[i]['Value'])

                    if isinstance(params[i]['Value'], bytes):
                        length += len(params[i]['Value'])
                    else:
                        length += (
                            struct.Struct(
                                (
                                    self.__endian
                                    + params[i]['DataType']
                                    )
                                ).size
                            )
        
        length += BASE_PTP_MSG_LENGTH

        cmdMsg = {
            'length' : {
                'DataType': 'L',
                'Value' : length
                },
            'MsgType' : {
                'DataType': 'H',
                'Value' : MsgType
                },
            'MsgOp' : {
                'DataType': 'H',
                'Value' : MsgOp
                },
            'TransactionId' : {
                'DataType': 'L',
                'Value' : self.transactionId
                },
            }
        
        if params:
            cmdMsg['Params'] = paramsMsg

        return cmdMsg
        
    def _choose_specific_camera(self, **kwargs):

        '''Select a specific camera
        '''

        idVendor = kwargs.get('idVendor')
        idProduct = kwargs.get('idProduct')

        return usb.core.find(
            idVendor=idVendor,
            idProduct=idProduct
            )
    
    def _setup_camera(self):

        for cfg in self.camera:

            for intf in cfg:

                if intf.bInterfaceClass == PTP_USB_CLASS:
                    
                    for EP in intf:
                        
                        ep_type = endpoint_type(EP.bmAttributes)
                        ep_dir = endpoint_direction(EP.bEndpointAddress)
                        
                        if ep_type == ENDPOINT_TYPE_BULK:
                            
                            if ep_dir == ENDPOINT_IN:
                                self.__inep = EP
                            elif ep_dir == ENDPOINT_OUT:
                                self.__outep = EP
                                self.out = EP
                        
                        elif ((ep_type == ENDPOINT_TYPE_INTR) and (ep_dir == ENDPOINT_IN)):
                            self.__intep = EP
                
                if not (self.__inep and self.__outep and self.__intep):
                    self.__inep = None
                    self.__outep = None
                    self.__intep = None
                
                else:
                    self.__cfg = cfg
                    self.__dev = self.camera
                    self.__intf = intf
                    logger.info('USB Camera Found and Connected')
                    return True
        
        logger.info('USB Camera not Found')
        return False

    def _encapsulate_msg(self, ptp_msg):

        msg = b''

        for i in ptp_msg.keys():

            if isinstance(ptp_msg[i]['Value'], list):
                for j in range(len(ptp_msg[i]['Value'])):
                    if isinstance(ptp_msg[i]['Value'][j], bytes):
                        msg += ptp_msg[i]['Value'][j]
                    else:
                        msg += struct.pack(
                            (
                                self.__endian
                                + ptp_msg[i]['DataType'][j]
                                ),
                            ptp_msg[i]['Value'][j]
                            )
                    

            elif isinstance(ptp_msg[i]['Value'], bytes):
                msg += ptp_msg[i]['Value']

            else:
                msg += struct.pack(
                    (
                        self.__endian
                        + ptp_msg[i]['DataType']
                        ),
                    ptp_msg[i]['Value']
                    )

        return msg

    def _send(self, ptp_msg, EP):
        '''Helper method for sending data.'''
        
        try:
            sent = 0
            while sent < len(ptp_msg):
                sent = EP.write(
                    # Up to 64kB
                    ptp_msg[sent:(sent + 64*2**10)]
                )
        except usb.core.USBError:
            pass

    def _receive(self, event=False):
        EP = self.__intep if event else self.__inep

        ptp_msg = b''

        reads = 0

        while len(ptp_msg) < BASE_PTP_MSG_LENGTH and reads < 5:

            ptp_msg += EP.read(EP.wMaxPacketSize)

            reads += 1
        
        msg_length = struct.unpack(
            (
                self.__endian
                + 'L'
                ),
            ptp_msg[:4])[0]

        while len(ptp_msg) < msg_length:
            ptp_msg +=  EP.read(
                min(
                    msg_length - BASE_PTP_MSG_LENGTH,
                    # Up to 64kB
                    64 * 2**10
                    )
                )

        return ptp_msg
    
    def __bin2ISO(self, val):
        '''Convert binary value of ISO to a readable string
        '''
        
        tmp = bin(val)[2:]
        
        if len(tmp) < 32:
            tmp = (
                '0' * (
                    32
                    - len(tmp)
                    )
                + tmp
                )
        
        ISOext = int(tmp[:-28],2)
        ISOmode = int(tmp[-28:-24],2)
        ISOval = int(tmp[-24:],2)

        ISO = ''

        if ISOmode != 0:
            ISO += self._decode_code(sony.SONY_ISO_MODE['Values'], ISOmode)
            ISO += ' '

        if ISOval == sony.SONY_ISO_AUTO:
            ISO += 'AUTO'
        else:
            ISO += str(ISOval)

        return ISO

    def __ISO2bin(self, val, mode=0, ext=0):

        if isinstance(val, str):

            if len(val) > 6:
                if val.find('_High') >=0:
                    mode_len = len('MultiFrameNR_High ')
                else:
                    if val.find('MultiFrameNR') >= 0:
                        mode_len = len('MultiFrameNR ')

                mode = val[:mode_len-1]
                val = val[mode_len:]

            if val.lower() == 'auto':
                val = sony.SONY_ISO_AUTO
            else:
                val = int(val)

        ISOval = str(bin(val)[2:])
        
        if len(ISOval) < 24:
            ISOval = (
                '0' * (
                    24
                    - len(ISOval)
                    )
                + ISOval
                )
        
        if isinstance(mode, str):
            ISOmode = str(bin(sony.SONY_ISO_MODE['Values'][mode])[2:])
        elif isinstance(mode, int):
            ISOmode = str(bin(mode)[2:])

        if len(ISOmode) < 4:
            ISOmode = (
                '0' * (
                    4
                    - len(ISOmode)
                    )
                + ISOmode
                )

        ISOext = str(bin(ext)[2:])

        if len(ISOext) < 4:
            ISOext = (
                '0' * (
                    4
                    - len(ISOext)
                    )
                + ISOext
                )

        ISOfinal = ISOext+ISOmode+ISOval

        return int(ISOfinal, 2)
    
    def __hex2mode(self, val):

        mode = self._decode_code(
            sony.SONY_EXPMODE['Values'],
            val
        )
        return mode
     
    def __hex2shutter(self, val):

        tmp = struct.pack(
            self.__endian+'L',
            val
            )

        num = struct.unpack(
            self.__endian
            + 'H', tmp[2:]
            )[0]
        
        den = struct.unpack(
            self.__endian
            + 'H', tmp[:2]
            )[0]
        
        if num >= den:
            return str(num/den)
        else:
            return str(num)+'/'+str(den)

    def __select_parser(self, key, val):

        if key == 'ISO':
            return self.__bin2ISO(val)
        elif key == 'ExposureProgramMode':
            return self.__hex2mode(val)
        elif key == 'ShutterSpeed':
            return self.__hex2shutter(val)

    def _property_msg(self, msg):

        vals = {}

        msg_len = 0

        vals['PropertyCode'] = struct.unpack(
            (
                self.__endian
                + 'H'
                ),
            msg[:2])[0]

        property_name = self._decode_code(self._PROPCODES['Values'], vals['PropertyCode'])

        if property_name in self.__available_parsers:
            parser = True
        else:
            parser = False

        msg_len += 2

        dataType = self._decode_datatype(
            PTPdb.PTP_DATATYPE['Values'],
            struct.unpack(
                (
                    self.__endian
                    + PTPdb.PTP_DATATYPE['DataType']
                    ),
                msg[msg_len:msg_len+2]
                )[0]
            )
        
        vals['DataType'] = copy.copy(dataType)

        dataType_len = struct.Struct(
            self.__endian
            + dataType
            ).size

        msg_len += 2

        if struct.unpack(self.__endian + 'B', msg[msg_len:msg_len+1])[0] == 1:
            vals['GetSet'] = 'GetSet'
        else:
            vals['GetSet'] = 'Set'

        msg_len += 1

        if self.camera.manufacturer == 'Sony':
            vals['Visibility'] = self._decode_code(
                sony.SONY_VISIBILITY['Values'],
                struct.unpack(
                    (
                        self.__endian
                        + 'B'
                    ),
                    msg[msg_len:msg_len+1]
                    )[0]
                )
            msg_len += 1

        val = struct.unpack(
            (
                self.__endian
                + dataType
            ),
            msg[msg_len:msg_len+dataType_len]
            )[0]

        if parser:
            val = self.__select_parser(property_name, val)

        vals['FactoryDefaultValue'] = val

        msg_len += dataType_len

        val = struct.unpack(
            (
                self.__endian
                + dataType
                ),
            msg[msg_len:msg_len+dataType_len]
            )[0]
        
        if parser:
            val = self.__select_parser(property_name, val)

        vals['CurrentValue'] = val

        msg_len += dataType_len

        vals['FmtFlag'] = struct.unpack(
            (
                self.__endian
                +'B'
            ),
            msg[msg_len:msg_len+1]
            )[0]

        msg_len += 1

        if vals['FmtFlag'] == 0:
            pass
        elif vals['FmtFlag'] == 1:
            tmp = struct.unpack(
                (
                    self.__endian
                    + 3*dataType
                    ),
                msg[msg_len:msg_len+dataType_len*3]
                )

            vals['MinValue'] = tmp[0]
            vals['MaxValue'] = tmp[1]
            vals['StepValue'] = tmp[2]

            msg_len += 3*dataType_len

        elif vals['FmtFlag'] == 2:
            fmt_len = struct.unpack(
                (
                    self.__endian
                    + 'H'
                    ),
                msg[msg_len:msg_len+2]
                )[0]

            msg_len += 2

            vals['AvailableValues'] = {}
            vals['AvailableValues']['Photo'] = []

            for _ in range(fmt_len):

                val = struct.unpack(
                    (
                        self.__endian
                        + dataType
                        ),
                    msg[msg_len:msg_len+dataType_len]
                    )[0]

                if parser:
                    val = self.__select_parser(property_name, val)

                vals['AvailableValues']['Photo'].append(val)

                msg_len += dataType_len

            tmp = struct.unpack(
                (
                    self.__endian
                    + 'H'
                    ),
                msg[msg_len:msg_len+2]
                )[0]

            if tmp < 0x1000:

                vals['AvailableValues']['Video'] = []

                fmt_len = copy.copy(tmp)

                msg_len += 2

                for _ in range(fmt_len):
                    
                    val = struct.unpack(
                        (
                            self.__endian
                            + dataType
                            ),
                        msg[msg_len:msg_len+dataType_len]
                        )[0]

                    if parser:
                        val = self.__select_parser(property_name, val)

                    vals['AvailableValues']['Video'].append(val)

                    msg_len += dataType_len

        return property_name, vals, msg_len

    def _all_properties_msg(self, msg):

        msg_len = struct.unpack(
            (
                self.__endian
                + 'Q'
            ),
            msg[:8]
            )[0]
        
        properties = {}

        msg_read = 8

        count = 0

        while count < msg_len:

            prop, vals, tmp = self._property_msg(msg[msg_read:])

            properties[prop] = vals

            msg_read += tmp
            count += 1

        return properties

    def _device_msg(self, msg):

        def ptp_array(msg, idx_start, ptp_length_type, data_type, \
                      char=False, decode=False, decoder=None):

            idx_temp = (
                struct.Struct(
                    (
                        self.__endian
                        + ptp_length_type
                        )
                    ).size
                + idx_start
                )

            data_length = struct.unpack(
                (
                    self.__endian
                    + ptp_length_type
                    ),
                msg[idx_start:idx_temp]
                )[0]

            idx_end = (
                struct.Struct(
                    (
                        self.__endian
                        + data_type
                        ).size
                    ) * data_length
                + idx_temp
                )
            
            
            values = struct.unpack(
                (
                    self.__endian
                    + data_type * data_length
                    ),
                msg[idx_temp:idx_end]
                )


            if char:
                tmp = ''
            else:
                
                tmp = []

            for k in values:
                if char:
                    if k == 0:
                        pass
                    else:
                        tmp += chr(k)
                else:
                    if decode:
                        tmp.append(self._decode_code(decoder, k))
                    else:
                        tmp.append(k)

            length = idx_end-idx_start

            return tmp, length


        vals = {}

        msg_len = 0

        vals['StandardVersion'] = struct.unpack(
            (
                self.__endian
                + 'H'
                ),
            msg[:2])[0]


        msg_len += 2

        vals['Vendor'] = self._decode_code(
            PTPdb.VENDOR['Values'],
            struct.unpack(
                (
                    self.__endian
                    + PTPdb.VENDOR['DataType']
                    ),
                msg[msg_len:msg_len+4]
                )[0]
            )
        
        msg_len += 4

        vals['VendorExtensionVersion'] = struct.unpack(
            (
                self.__endian
                + 'H'
                ),
            msg[msg_len:msg_len+2])[0]

        msg_len += 2

        vals['VendorExtensionDesc'], tmp = ptp_array(
            msg[msg_len:], msg_len, 'B', 'H', char = True
            )

        msg_len += tmp

        vals['FunctionalMode'] = struct.unpack(
            (
                self.__endian
                + 'H'
                ),
            msg[msg_len:msg_len+2])[0]

        msg_len += 2

        vals['OperationsSupported'], tmp = ptp_array(
            msg[msg_len:], msg_len, 'L', PTPdb.PTP_OPCODE['DataType'],
            decode = True, decoder = PTPdb.PTP_OPCODE['Values']
            )

        msg_len += tmp

        vals['EventsSupported'], tmp = ptp_array(
            msg[msg_len:], msg_len, 'L', PTPdb.PTP_EVENTCODE['DataType'],
            decode = True, decoder = PTPdb.PTP_EVENTCODE['Values']
            )

        msg_len += tmp

        vals['DevicePropertiesSupported'], tmp = ptp_array(
            msg[msg_len:], msg_len, 'L', PTPdb.PTP_PROPCODE['DataType'],
            decode = True, decoder = PTPdb.PTP_PROPCODE['Values']
            )

        msg_len += tmp

        vals['CaptureFormat'], tmp = ptp_array(
            msg[msg_len:], msg_len, 'L', PTPdb.PTP_OBJFMTCODE['DataType'],
            decode = True, decoder = PTPdb.PTP_OBJFMTCODE['Values']
            )

        msg_len += tmp

        vals['ImageFormat'], tmp = ptp_array(
            msg[msg_len:], msg_len, 'L', PTPdb.PTP_OBJFMTCODE['DataType'],
            decode = True, decoder = PTPdb.PTP_OBJFMTCODE['Values']
            )

        msg_len += tmp

        vals['Manufacturer'], tmp = ptp_array(
            msg[msg_len:], msg_len, 'B', 'H', char = True
            )

        msg_len += tmp

        vals['Model'], tmp = ptp_array(
            msg[msg_len:], msg_len, 'B', 'H', char = True
            )

        msg_len += tmp

        vals['DeviceNumber'], tmp = ptp_array(
            msg[msg_len:], msg_len, 'B', 'H', char = True
            )

        msg_len += tmp

        vals['SerialNumber'], tmp = ptp_array(
            msg[msg_len:], msg_len, 'B', 'H', char = True
            )

        msg_len += tmp

        return vals
    
    def _decode_code(self, codes_dict, code):
        try:
            code_name = list(codes_dict.keys())[list(codes_dict.values()).index(code)]
        except ValueError:
            code_name = 'Unknown : ' + str(hex(code))

        return code_name

    def _decode_datatype(self, codes_dict, code):
        try:
            idx = list(map(lambda x: x['Code'], codes_dict.values())).index(code)
            code_name = list(codes_dict.keys())[idx]
        except ValueError:
            code_name = 'Unknown : ' + str(hex(code))

        return code_name
    
    def _decode_msg(self, PTPmsg):

        msg = {}

        idx_start = 0

        for i in MSG_STRUCT.keys():

            if i == 'Payload':
                if len(PTPmsg) > BASE_PTP_MSG_LENGTH:

                    if msg['MsgType'] == 'Response':
                        msg['Payload'] = struct.unpack(
                            (
                                self.__endian
                                + 'L'
                                ),
                            PTPmsg[idx_start:]
                            )
                    
                    elif msg['MsgType'] == 'Data':
                        #Data Message are parsed only if required
                        msg[i] = PTPmsg[idx_start:]
            
            else:

                idx_end = (
                    struct.Struct(
                        (
                            self.__endian
                            + MSG_STRUCT[i]
                            )
                        ).size
                    + idx_start
                    )

                msg[i] = struct.unpack(
                    (
                        self.__endian
                        + MSG_STRUCT[i]
                        ),
                    PTPmsg[idx_start:idx_end]
                    )[0]

                if i == 'MsgType':
                    msg[i] = list(USB_OPERATIONS.keys())[list(USB_OPERATIONS.values()).index(msg[i])]
                
                elif i == 'OpCode':
                    
                    if msg['MsgType'] == 'Response':
                        msg['RespCode'] = self._decode_code(self._RESPCODES['Values'], msg[i])
                    else:
                        msg[i] = self._decode_code(self._OPCODES['Values'], msg[i])

                idx_start = copy.copy(idx_end)
        
        return msg
        
    def _session_handler(self):

        self.sessionId += 1

        params = {
            'Msg' : {
                'Value': self.sessionId,
                'DataType': 'L'
            }
        }

        if not self._session_open:
            cmd = self._OPCODES['Values']['OpenSession']
        else:
            cmd = self._OPCODES['Values']['CloseSession']

        PTPmsg, _ = self.sendMsg(
            USB_OPERATIONS['Command'],
            cmd,
            params = params,
            receive = True
            )

        resp = self._decode_msg(PTPmsg)

        if resp['MsgType'] == 'Response':
            if resp['RespCode'] == 'OK':
                self._session_open = not self._session_open
                if self._session_open:
                    logger.info('Open Session to Camera')
                else:
                    logger.info('Close Session to Camera')
            else:
                if not self._session_open:
                    logger.info('Cannot Open Session to Camera')
                else:
                    logger.info('Cannot Close Session to Camera')

        self.transactionId += 1

    def _handshake(self, count, key1 = 0, key2 = 0):

        params = {
            'Msg' : {
                'Value': [count, key1, key2],
                'DataType': ['L']*3
            }
        }

        _ = self.sendMsg(
            USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SDIOConnect'],
            params= params,
            receive = True
            )

        resp = self._decode_msg(self._receive())

        self.transactionId += 1

        if resp['MsgType'] == 'Response':
            return resp['RespCode']
        else:
            return None

    def _sony_info(self, code=0x12c):

        params = {
            'Msg' : {
                'Value': code,
                'DataType': 'L'
            }
        }

        _ = self.sendMsg(
            USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SDIOGetExtDeviceInfo'],
            params= params,
            receive = True
            )

        resp = self._decode_msg(self._receive())

        self.transactionId += 1

        if resp['MsgType'] == 'Response':
            return resp['RespCode']
        else:
            return None
 
    def sendMsg(self, MsgType, opId, params = None, receive = True, data = None, event = False, timing = False, timeout = 0.004):

        EP = self.__intep if event else self.__outep

        PTPmsgOut = self._PTPMsg(MsgType, opId, params)

        PTPbyteMsg = self._encapsulate_msg(PTPmsgOut)

        if data:
            dataMsg = self._PTPMsg(USB_OPERATIONS['Data'], opId, data)

            databyeMsg = self._encapsulate_msg(dataMsg)
            self._send(PTPbyteMsg, EP)
            if timing:
                timing = time.time()
            self._send(databyeMsg, EP)
        else:
            self._send(PTPbyteMsg, EP)

        if receive:
            time.sleep(timeout)
            PTPmsgIn = self._receive()

        return PTPmsgIn, timing
  
    def initialize_camera(self):

        self._session_handler()

        resp = []

        resp.append(self._handshake(1))
        resp.append(self._handshake(2))
        resp.append(self._sony_info())
        resp.append(self._handshake(3))
        resp.append(self._sony_info())

        if all(list(map(lambda r: r == 'OK', resp))):
            logger.info('Camera Initialized Correctly')
        else:
            logger.info('Camera Not Initialized Correctly')

        time.sleep(0.035)

        self.camera_properties = self.get_camera_properties()

        mode = self.camera_properties['ExposureProgramMode']['CurrentValue']

        if any(md in mode for md in self.__video_modes):
            self._current_mode = 'Video'
        else:
            self._current_mode = 'Photo'
    
    def close(self):

        self._session_handler()

        if not self._session_open:
            logger.info('Camera Closed Correctly')
  
    def get_device_info(self):

        PTPmsg, _ = self.sendMsg(
            USB_OPERATIONS['Command'],
            self._OPCODES['Values']['GetDeviceInfo'],
            receive = True
            )

        _ = self._receive()

        resp = self._decode_msg(PTPmsg)

        vals = self._device_msg(resp['Payload'])

        return vals

    def get_camera_properties(self):

        params = {
            'Msg' : {
                'Value': self.__camera_prop_code,
                'DataType': 'L'
            }
        }

        PTPmsg, _ = self.sendMsg(
            USB_OPERATIONS['Command'],
            self._OPCODES['Values']['GetAllDevicePropData'],
            params=params,
            receive = True
            )

        _ = self._receive()

        resp = self._decode_msg(PTPmsg)

        vals = self._all_properties_msg(resp['Payload'])

        self.transactionId += 1

        return vals

    def capture_photo(self):

        params = {
            'Msg' : {
                'Value': self._PROPCODES['Values']['Capture'],
                'DataType': self._PROPCODES['DataType']
            }
        }

        down = {
            'Msg' : {
                'Value': sony.SONY_BUTTON['Values']['Down'],
                'DataType': sony.SONY_BUTTON['DataType']
            }
        }

        up = {
            'Msg' : {
                'Value': sony.SONY_BUTTON['Values']['Up'],
                'DataType': sony.SONY_BUTTON['DataType']
            }
        }

        resp = []

        resp1, timing = self.sendMsg(
            USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SetControlDeviceB'],
            params=params,
            data=down,
            timing=True
            )

        self.transactionId += 1
        
        time.sleep(0.003)

        resp2, _ = self.sendMsg(
            USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SetControlDeviceB'],
            params=params,
            data=up
            )

        self.transactionId += 1

        resp1 = self._decode_msg(resp1)
        resp2 = self._decode_msg(resp2)

        if resp1['MsgType'] == 'Response':
            resp.append(resp1['RespCode'])
        if resp2['MsgType'] == 'Response':
            resp.append(resp2['RespCode'])

        if len(resp) == 2:
            if all(list(map(lambda r: r == 'OK', resp))):
                logger.info(f'Photo Captured at {timing}')
            else:
                logger.info('Photo not Captured')
        else:
            logger.info('Did not get response from Commands')

    def set_camera_mode(self, mode = 'Photo_M'):

        params = {
            'Msg' : {
                'Value': self._PROPCODES['Values']['ExposureProgramMode'],
                'DataType': self._PROPCODES['DataType']
            }
        }

        mode_dict = {
            'Msg' : {
                'Value': sony.SONY_EXPMODE['Values'][mode],
                'DataType': sony.SONY_EXPMODE['DataType']
            }
        }

        PTPmsg, _ = self.sendMsg(
            USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SetControlDeviceA'],
            params=params,
            data=mode_dict,
            )

        resp = self._decode_msg(PTPmsg)

        if any(md in mode for md in self.__video_modes):
            self._current_mode = 'Video'
        else:
            self._current_mode = 'Photo'

        if resp['MsgType'] == 'Response':
            if resp['RespCode'] == 'OK':
                logger.info(f'Set Camera mode: {self._current_mode}_{mode}')
            else:
                logger.info(f'Impossible to set Camera mode to {mode}')

        self.transactionId += 1

        self.camera_properties = self.get_camera_properties()

    def video_control(self):

        params = {
            'Msg' : {
                'Value': self._PROPCODES['Values']['Movie'],
                'DataType': self._PROPCODES['DataType']
            }
        }

        down = {
            'Msg' : {
                'Value': sony.SONY_BUTTON['Values']['Down'],
                'DataType': sony.SONY_BUTTON['DataType']
            }
        }

        up = {
            'Msg' : {
                'Value': sony.SONY_BUTTON['Values']['Up'],
                'DataType': sony.SONY_BUTTON['DataType']
            }
        }

        resp = []

        resp1, timing = self.sendMsg(
            USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SetControlDeviceB'],
            params=params,
            data=down,
            timing=True
            )

        self.transactionId += 1
        
        time.sleep(0.003)

        resp2, _ = self.sendMsg(
            USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SetControlDeviceB'],
            params=params,
            data=up
            )

        self.transactionId += 1

        resp1 = self._decode_msg(resp1)
        resp2 = self._decode_msg(resp2)

        if resp1['MsgType'] == 'Response':
            resp.append(resp1['RespCode'])
        if resp2['MsgType'] == 'Response':
            resp.append(resp2['RespCode'])

        self._recording_status = not self._recording_status
        if self._recording_status:
            self.__video_status = 'Started'
        else:
            self.__video_status = 'Stopped'

        if len(resp) == 2:
            if all(list(map(lambda r: r == 'OK', resp))):
                logger.info(f'Video Recording {self.__video_status} at {timing}')
            else:
                logger.info('Video Command Failed')
        else:
            logger.info('Did not get response from Commands')

    def set_iso(self, value):

        if isinstance(value, int) or isinstance(value, float):
            mode = 0
            ext = 0

        elif isinstance(value, list):
            if len(value) > 2:
                ext = value[2]

            mode = value[0]
            value = value[1]
        
        available_ISO = list(
            map(
                lambda x: self.__ISO2bin(x),
                self.camera_properties['ISO']['AvailableValues'][self._current_mode]
            )
        )

        newISO = self.__ISO2bin(value, mode, ext)

        if newISO not in available_ISO:
            tmp = list(
                map(
                    lambda x: abs(x-newISO),
                    available_ISO
                    )
                )
            idx = tmp.index(min(tmp))

            newISO = available_ISO[idx]

            tmp = self.__bin2ISO(newISO)

            logger.info(f'Choose the closest ISO, {tmp}, to the one selected {value}')

        
        params = {
            'Msg' : {
                'Value': self._PROPCODES['Values']['ISO'],
                'DataType': self._PROPCODES['DataType']
            }
        }

        mode = {
            'Msg' : {
                'Value': newISO,
                'DataType': 'L'
            }
        }

        PTPmsg, _ = self.sendMsg(
            USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SetControlDeviceA'],
            params=params,
            data=mode,
            )

        resp = self._decode_msg(PTPmsg)

        if resp['MsgType'] == 'Response':
            if resp['RespCode'] == 'OK':
                logger.info(f'Set New ISO: {value}')

        self.transactionId += 1

        time.sleep(0.035)

        self.camera_properties = self.get_camera_properties()

    def _single_step_focus_distance(self, further=True):

        if further:
            value = 1
        else:
            value = -1

        params = {
            'Msg' : {
                'Value': self._PROPCODES['Values']['FocusDistance'],
                'DataType': self._PROPCODES['DataType']
            }
        }

        mode = {
            'Msg' : {
                'Value': value,
                'DataType': 'h'
            }
        }

        PTPmsg, _ = self.sendMsg(
            USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SetControlDeviceB'],
            params=params,
            data=mode,
            )

        resp = self._decode_msg(PTPmsg)

        self.transactionId += 1

        if resp['MsgType'] == 'Response':
            if resp['RespCode'] == 'OK':
                return 'OK'
        else:
            return 'NO'

    def set_focus_distance(self, nstep, further=True):

        resp = []

        for _ in range(nstep):
            resp.append(self._single_step_focus_distance(further))
            time.sleep(0.3)
        
        if all(list(map(lambda r: r == 'OK', resp))):
            if nstep > 85:
                if further:
                    logger.info('Set Focus to Infinity')
                else:
                    logger.info('Set Focus to Close')
            else:
                if further:
                    logger.info(f'Set Focus further by {nstep}')
                else:
                    logger.info(f'Set Focus closer by {nstep}')
        else:
            logger.info('Cannot Set Focus Distance')
    
    def set_focus_infinity(self):

        self.set_focus_distance(100)

    def set_shutter_speed(self, value):

        if isinstance(value, float) or isinstance(value, int):
            value = value
        
        available_shutter = list(
            map(
                lambda x: float(Fraction(x)),
                self.camera_properties['ShutterSpeed']['AvailableValues'][self._current_mode]
            )
        )

        if value not in available_shutter:
            tmp = list(
                map(
                    lambda x: abs(x-value),
                    available_shutter
                    )
                )
            idx = tmp.index(min(tmp))

            old = copy.copy(value)

            value = available_shutter[idx]

            logger.info(f'Choose the closest Shutter Speed, {value}, to the one selected {old}')


        num, den = decimal.Decimal(str(value)).as_integer_ratio()

        num_bytes = struct.pack(
            self.__endian
            + 'H', num
            )
        
        den_bytes = struct.pack(
            self.__endian
            + 'H', den
            )

        val = den_bytes+num_bytes

        params = {
            'Msg' : {
                'Value': self._PROPCODES['Values']['ShutterSpeed'],
                'DataType': self._PROPCODES['DataType']
            }
        }

        mode = {
            'Msg' : {
                'Value': val,
                'DataType': 'NA'
            }
        }

        PTPmsg, _ = self.sendMsg(
            USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SetControlDeviceA'],
            params=params,
            data=mode,
            )

        resp = self._decode_msg(PTPmsg)

        if resp['MsgType'] == 'Response':
            if resp['RespCode'] == 'OK':
                logger.info(f'Set New Shutter Speed: {value}')
            
        self.transactionId += 1

        time.sleep(0.05)

    def set_datetime(self, event = False, timeout = 0.04, delta = 1e-3):

        params = {
            'Msg' : {
                'Value': self._PROPCODES['Values']['DateTime'],
                'DataType': self._PROPCODES['DataType']
            }
        }

        cmdMsg = self._PTPMsg(
            USB_OPERATIONS['Command'],
            self._OPCODES['Values']['SetControlDeviceA'],
            params
            )
        
        cmdMsg = self._encapsulate_msg(cmdMsg)

        msgData_length = struct.pack('<L', 61)

        msgType = struct.pack('<H', USB_OPERATIONS['Data'])
        msgCode = struct.pack('<H', self._OPCODES['Values']['SetControlDeviceA'])
        msgTrans = struct.pack('<L', self.transactionId)
        msgDate_Length = struct.pack('<B', 48)

        dataMsg = (
            msgData_length
            + msgType
            + msgCode
            + msgTrans
            + msgDate_Length
        )


        EP = self.__intep if event else self.__outep

        count = 0

        _ = EP.write(cmdMsg)
        while True:
            t = time.time()
            time.sleep(math.ceil(t)-t)
            if abs(time.time()-math.floor(t))-1 < delta:
                timing = time.time()
                _ = EP.write(
                    dataMsg
                    + datetime.datetime.fromtimestamp(math.ceil(t)).astimezone().strftime("%Y%m%dT%H%M%S.0%z").encode('utf-16LE')+b'\x00\x00\x00\x00'
                    )
                break
            count += 1
            if count == 10:
                delta *= 2
        

        time.sleep(timeout)
        PTPmsgIn = self._receive()

        resp = self._decode_msg(PTPmsgIn)

        if resp['MsgType'] == 'Response':
            if resp['RespCode'] == 'OK':
                logger.info(f'Set camera DateTime to {datetime.datetime.fromtimestamp(math.ceil(t)).astimezone().strftime("%Y-%m-%d %H:%M:%S.%f")}')
                logger.info(f'Loop accuracy for Timing: {delta*1000} ms')
                logger.info(f'Command Sent at {datetime.datetime.fromtimestamp(timing).astimezone().strftime("%Y-%m-%d %H:%M:%S.%f")}')
                logger.info(f'Predicted Accuracy: {(timing-math.ceil(t)+delta)*1000} ms')
            
        self.transactionId += 1








    
