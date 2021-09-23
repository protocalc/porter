from digi.xbee.devices import XBeeDevice
from digi.xbee.serial import XBeeSerialPort

class antenna:

    '''
    Class to configure parameters of a xbee antenna 
    '''

    def __init__(self, port, baudrate=9600):

        self.port = port
        self.baudrate = baudrate

        self.device = XBeeDevice(self.port, self.baudrate)

    def change_baudrate(self, new_baudrate):

        xbee_ser = XBeeSerialPort(self.baudrate, self.port)
        xbee_ser.set_baudrate(new_baudrate)

        self.baudrate = new_baudrate

        self.device = XBeeDevice(self.port, self.baudrate)

    def set_param(self, parameter, value):

        '''
        Generic function to set a parameter for a xbee antenna
        '''

        self.device.set_parameter(parameter, bytearray(value, 'utf-8'))

    def set_role(self, role):

        '''
        Set the role for the xbee antenna. 
        Parameter:
        - role: str. Possible to choose between 'join' or 'form'
        '''

        available_roles = ['join', 'form']

        if role in available_roles:

            if role == 'join':
                value = 0
            elif role == 'form':
                value = 1

            self.set_param('CE', value)

class comms:

    def __init__(self, local_xbee_port, local_xbee_baudrate, remote_xbee_id=None):

        if local_xbee_port is None and local_xbee_baudrate is None:
            self.local_xbee = None
        else:
            self.local_xbee = XBeeDevice(local_xbee_port, local_xbee_baudrate)
            self.local_xbee.open()

            self.remote_xbee_id = remote_xbee_id

            xbee_network = self.local_xbee.get_network()
            self.remote_xbee = xbee_network.discover_device(self.remote_xbee_id)

    def send_msg(self, msg):

        if isinstance(msg, list):
            temp = ''
            for i in msg:
                temp += i
            msg = temp

        if len(msg)>255:
            while len(msg) > 0:
                self.local_xbee.send_data(self.remote_xbee, msg[:255])
                msg = msg[255:]
        else:
            self.local_xbee.send_data(self.remote_xbee, msg)
        
    def poll_msg(self):

        msg = b''

        while True:
            temp = self.local_xbee.read_data()
            if msg is not None:
                msg += temp
                if msg[-3:].decode('utf-8') == 'END':
                    dest = msg[:3].decode('utf-8')
                    msg = msg.data[3:-3]
                    break

        return dest, msg

    

        

