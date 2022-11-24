import minimalmodbus as mm
import struct
import time

freq_dict = {
    '1': 0.125,
    '2': 0.25,
    '3': 0.5,
    '4': 1,
    '5': 2,
    '6': 4,
    '7': 8,
    '8': 16
}

class inclinometer:

    def __init__(self, port, modbus_address, baud = 38400):

        self.instrument = mm.Instrument(port, modbus_address)
        self.instrument.serial.baudrate = baud

        self.zero_angles = [0, 0]

    def get_angle(self, axis):

        if axis.lower() == 'x':
            start_reg = 0
        elif axis.lower() == 'y':
            start_reg = 2

        return self.instrument.read_long(start_reg, signed=True)/1000

    def read_msg(self, return_binary=False, time_info=True):

        ang = self.instrument.read_registers(0, 4)
        t = time.time()

        if return_binary:
            data = struct.pack('>HHHH', *ang)
        else:
            ang_x, ang_y = struct.unpack('>ll', struct.pack('>HHHH', *ang))

            data = (ang_x/1000, ang_y/1000)

        if time_info:
            return [t, data]
        else:
            data

    def get_temperature(self):

        return self.instrument.read_register(7, signed=True)/100

    def get_filter(self):

        return freq_dict[str(int(self.instrument.read_register(9)))]

    def change_freq_filter(self, freq):

        freq_list = list(freq_dict.values())

        if freq in freq_list:

            key = 1+freq_list.index(freq)
            val = freq_dict[str(int(key))]

            self.instrument.write_register(9, val, functioncode=6)

    def set_zero(self, reset='True'):

        self.instrument.serial.timeout = 0.5

        if not reset:
            self.zero_angles = list(self.get_xy_angles())
            self.instrument.write_register(20, 1, functioncode=6)
        else:
            self.instrument.write_register(20, 0, functioncode=6)

    def get_zero_status(self):

        status = self.instrument.read_register(20)

        if status == 0:
            print('The device is set to absolute measurments')
        else:
            print('The device is set to relative measurments' + \
                  'with zero {:.2f} and {:.2f}'.format(*self.zero_angles))

    def close_connection(self):
        self.instrument.serial.close()
