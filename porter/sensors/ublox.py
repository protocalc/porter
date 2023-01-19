import serial
import pickle
import logging
import time
import struct

import numpy as np

import sensors.ublox_utils as ubx_utils

logger = logging.getLogger()

class UBX:

    def __init__(self, port=None, baudrate=None, serial_connection=None, **kwargs):

        """ Connect to a ublox module using a serial connection.

        Default baudrate for UBlox modules is 38400

        Args:
            port (str): string with the port address of the UBlox Sensor
            baudrate (int): baudrate for the UBlox module
            serial_connection (serial.Serial): serial connection to the UBlox module
        """

        if serial_connection is None:
            if port is not None and baudrate is not None:
                self.port = port
                self.conn = serial.Serial(self.port, baudrate)
        else:
            self.conn = serial_connection

        name = kwargs.get('name', 'Generic UBlox')
        
        logging.info(f'Connected to the UBLOX sensor {name}')

    def save_binary(self, chunks_size=10, filename='attitude_binary', max_bytes=None):

        """
        Read continuosly the serial port and then save the data on a pickle file.
        Data are saved as read, so they are in binary format
        Parameters:
        - chunks_size: int, the number of byte to read each time from the
                       serial port
        - filename: str, the name of the pickle file to be create
        - max_bytes: int, the maximum number of bytes to read from the serial port
        """

        """
        Add saving NMEA data
        """

        count = 0

        pck = open(filename, 'ab')
        while True:

            pickle.dump(self.conn.read(chunks_size), pck)
            
            if max_bytes is not None:
                if int(max_bytes/chunks_size) < count:
                    break
            count += 1
    
    def stream(self, stream_len=None, save_data=False, print_data=True, filename='attitude'):

        import h5py

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

        while True:

            if count == 0:
                msg = self.read_msg()
            else:
                msg = self.read_msg(first_msg=False)

            if isinstance(msg, bytes):
                ubxmsg = ubx_utils.UBXMessage()
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
                if line[-2:] == ubx_utils.HEADER:
                    msg_cat = 'ubx'
                    break
                else:
                    if line[-1:] == ubx_utils.RTCM_HEADER:
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

    def class2char(self, msg_class):
        
        if isinstance(msg_class, list):
            class_char = []
            for i in range(len(msg_class)):
                class_char.append(ubx_utils.ubx_dict[msg_class[i]]['char'])
        else:
            class_char = ubx_utils.ubx_dict[msg_class]['char']

        return class_char

    def id2char(self, msg_class, msg_id):
        
        if isinstance(msg_id, list):
            id_char = []
            for i in range(len(msg_id)):
                id_char.append(ubx_utils.ubx_dict[msg_class][msg_id[i]]['char'])
        else:
            id_char = ubx_utils.ubx_dict[msg_class][msg_id]['char']

        return id_char

    def read_first_msg(self, **kwargs):

        """
        Read the first message availble from a UBlox device
        """

        msg_cat = kwargs.get('msg_cat', None)
        first_msg = kwargs.get('first_msg', True)
        decode = kwargs.get('decode', False)
        time_info = kwargs.get('time_info', True)

        if msg_cat is None:
            if first_msg:
                cat = self.find_header()
                if cat == 'ubx':
                    msg_cat = ubx_utils.HEADER
                elif cat == 'nmea':
                    msg_cat = b'$'
                elif cat == 'rtcm':
                    msg_cat = ubx_utils.RTCM_HEADER
            else:
                msg_cat = self.conn.read(2)
        else:
            if msg_cat == 'ubx':
                msg_cat = ubx_utils.HEADER
            elif msg_cat == 'nmea':
                msg_cat = b'$'
            elif msg_cat == 'rtcm':
                msg_cat = ubx_utils.RTCM_HEADER

        if msg_cat == ubx_utils.HEADER:
            pre = self.conn.read(4)
            msg_length = struct.unpack('<H', pre[-2:])

            final_msg = self.conn.read(msg_length[0]+2)
            t = time.time()
            final_msg = msg_cat+pre+final_msg

            if decode:
                ubxmsg = ubx_utils.UBXMessage()
                ubxmsg.decode(final_msg)
                name, fields, values = ubxmsg.name, \
                    ubxmsg.fields_name, \
                    ubxmsg.values

                final_msg = (name, fields, values)

        else:
            if len(msg_cat) != 1:
                msg_cat_temp = msg_cat[0:1]
            else:
                msg_cat_temp = msg_cat

            if msg_cat_temp == b'$':
                msg = self.conn.read_until(expected=b'\r\n')
                t = time.time()

                if decode:
                    final_msg = (msg_cat+msg).decode('utf-8')
                else:
                    final_msg = msg_cat+msg

            elif msg_cat_temp == ubx_utils.RTCM_HEADER:
                
                if len(msg_cat) != 1:
                    pre = msg_cat[1:]+self.conn.read(1)
                else:
                    pre = self.conn.read(2)

                msg_length = struct.unpack('!H', pre)
                msg_length = 0x03ff & msg_length[0]

                final_msg = self.conn.read(msg_length+3)
                t = time.time()
                final_msg = msg_cat[0]+pre+final_msg

        if time_info:
            return [t, final_msg]
        else:
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
                    ubx_id = list(ubx_utils.ubx_dict[ubx_class].keys())
                    ubx_id = ubx_id[1:]

                    id_char = self.id2char(ubx_class, ubx_id)

                else:
                    if isinstance(ubx_id, str):
                        id_char = ubx_utils.ubx_dict[ubx_class][ubx_id]['char']
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

                        vals = ubx_utils.HEADER+pre+final_msg
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
                    vals = ubx_utils.RTCM_HEADER+pre+final_msg
                    break

        elif msg_cat == 'nmea':
            while True:
                cat = self.find_header()
                if cat == 'nmea':
                    final_msg = self.conn.read_until(expected=b'\r\n')

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

            if line[-2:] == ubx_utils.HEADER:
                
                pre = self.conn.read(2)

                if pre[0:1] == msg_class:
                    if pre[1:2] in msg_id:
                        length = self.conn.read(2)

                        payload = self.conn.read(struct.unpack('<H', length)[0])
                        chk = self.conn.read(2)

                        msg = ubx_utils.HEADER+pre+length+payload+chk

                        ubxmsg = ubx_utils.UBXMessage()
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

        payload_template = ubx_utils.ubx_dict[msg_class][msg_id]['payload']
        
        if isinstance(vals, dict):
            if len(vals.keys()) != len(payload_template.keys()):
                print('ERROR', payload_template.keys())
                return 0

        ubxmsg = ubx_utils.UBXMessage(msg_class=msg_class, msg_id=msg_id)

        ubxmsg.encode(vals)

        self.conn.write(ubxmsg.ubx_msg)

        if ack:
            self.read_single_msg(msg_cat ='ubx', ubx_class='ACK')

class UBXconfig:

    def __init__(self, port=None, baudrate=None, serial_connection=None, **kwargs):
        
        if serial_connection is None:
            if port is not None and baudrate is not None:
                self.port = port
                self.conn = serial.Serial(self.port, baudrate)
        else:
            self.conn = serial_connection

        name = kwargs.get('name', 'Generic UBlox')
        
        logging.info(f'Configuring UBLOX sensor {name}')

    def configure(self, config):

        for i in config.keys():
            if 'survey' == i.lower():
                if config['Survey'][0].lower() == 'enable':
                    self.enableSurvey(config['Survey'][1], config['Survey'][2])
                elif config['Survey'][0].lower() == 'disable':
                    self.disableSurvey()
            elif i.lower() == 'baudrate':
                self.change_baudrate(config['Baudrate'][0], config['Baudrate'][1])
            elif i.lower() == 'rtcm':
                for j in config['RTCM'].keys():
                    if config['RTCM'][j].lower() == 'output':
                        self.confRTCMmsg_output(config['RTCM'][j]['uart_port'], config['RTCM'][j][1])
                    elif config['RTCM'][j].lower() == 'input':
                        self.confRTCMmsg_input(config['RTCM'][j])
            elif i.lower() == 'ubx_msg':

                output_port = config['UBX_MSG']['output_port']

                if output_port[0].lower() == 'uart':
                    port_string = 'UART'+str(int(output_port[1]))
                else:
                    port_string = output_port[0]

                string = 'CFG_MSGOUT_UBX_'
                
                for j in config['UBX_MSG'].keys():
                    if j.lower() == 'output_port':
                        pass
                    else:
                        group = []
                        for k in config['UBX_MSG'][j]:
                            string = (
                                string
                                + j
                                + '_'
                                + k
                                + '_'
                                + port_string
                            )

                            group.append(
                                (string, 1)
                            )

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
                            "group": group
                        }

                        self.conn.write_msg('CFG', 'VALSET', msg_dict, True)
            
            elif i.lower() == 'nmea' or i.lower() == 'ubx':

                if config[i]['output']['set']:
                    output = 1
                else:
                    output = 0

                string = (
                    'CFG_'
                    + config[i]['output']['port']
                    + 'OUTPROT_'
                    + i
                )

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
                    "group": [(string, output)]
                }

                self.conn.write_msg('CFG', 'VALSET', msg_dict, True)

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

        self.conn.write_msg('CFG', 'VALSET', msg_dict, True)
        self.conn.conn.close()

        self.baudrate = baudrate_new

        self.conn = UBX(self.port, self.baudrate)

    def enableSurvey(self, survey_time, survey_accuracy):

        """
        Enable Survey Mode for initializing an RTK base:
        Parameters:
        - survey_time: float. Time for the survey in seconds
        - survey_accuracy: float. Accuracy required for the survey in meters
        """

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

        self.conn.write_msg('CFG', 'VALSET', survey_dict, True)

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

        self.conn.write_msg('CFG', 'VALSET', survey_dict, True)

    def confRTCMmsg_output(self, uart_port=2, usb=True):

        """
        Configure the output of required RTCM messages.
        Optional:
        - uart_port: int. Choose between the UART 1 and 2 as output of
                     RTCM messages
        """
        
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

        self.conn.write_msg('CFG', 'VALSET', RTCM_dict, True)

    def confRTCMmsg_input(self, uart_port=2):

        """
        Configure the option to input RTCM messages.
        Optional:
        - uart_port: int. Choose between the UART 1 and 2 as input of
                     RTCM messages
        """
        
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

        self.conn.write_msg('CFG', 'VALSET', RTCM_dict, True)

    def configure_frequency(self, freq):

        """
        Set the frequency of the update for the navigation solution
        Parameter:
        - freq: float. Frquency of the update in Hz
        """

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

        self.conn.write_msg('CFG', 'VALSET', update_dict, True)
