from digi.xbee.devices import XBeeDevice
from digi.xbee.serial import XBeeSerialPort

# OBI  id: 0013A20041C2BB3E
# LUKE id: 0013A20041C2B524

class Xbee:
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
        self.device.set_parameter(parameter, bytearray(value, 'utf-8'))

    def set_role(self, role):
        available_roles = ['join', 'form']
        if role in available_roles:
            if role == 'join':
                value = 0
            elif role == 'form':
                value = 1
            self.set_param('CE', value)

    def open(self, force_settings=False, remote_xbee_id=None):
        self.remote_device_id = remote_xbee_id
        self.device.open(force_settings=force_settings)
        self.device.add_data_received_callback(self.data_receive_callback)
        network = self.device.get_network()
        self.remote_device = network.discover_device(self.remote_device_id)

    def close(self):
        self.device.close()

    def data_receive_callback(self, msg):
        addr = msg.remote_device.get_64bit_addr()
        data = msg.data.decode("utf-8", errors="ignore")
        print(f"Received from {addr}: {data}")
    
    def send_msg(self, msg):
        if isinstance(msg, list):
            temp = ''
            for i in msg:
                temp += i
            msg = temp
        if len(msg)>255:
            while len(msg) > 0:
                self.device.send_data(self.remote_device, msg[:255])
                msg = msg[255:]
        else:
            self.device.send_data(self.remote_device, msg)

    def send_msg_broadcast(self, msg):
        if isinstance(msg, list):
            temp = ''
            for i in msg:
                temp += i
            msg = temp
        if len(msg)>255:
            while len(msg) > 0:
                self.device.send_data_broadcast(msg[:255])
                msg = msg[255:]
        else:
            self.device.send_data_broadcast(msg)
    
    def poll_msg(self):
        msg = b''
        while True:
            temp = self.device.read_data()
            if temp is not None:
                msg += temp.data
                if msg[-3:].decode('utf-8') == 'END':
                    msg = msg[:-3]
                    break
        return msg