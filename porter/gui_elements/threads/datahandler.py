from PyQt5 import QtCore
import copy
import struct
import ublox.ublox as ublox

class datahandler(QtCore.QObjects):

    data = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

    def run(self):
        pass
    
    @QtCore.pyqtSlot(list)
    def handler(self, lst):

        lst = copy.copy(lst)

        if lst[0] == 'UBX':
            ubxmsg = ublox.UBXMessage(msg=lst[1])
            '''
            ADD extraction of only NAV data
            '''
            if ubxmsg.msg_class == 'NAV':
                if ubxmsg.msg_id == 'HPPOSLLH': ### CHECK ###
                    val = dict(zip(ubxmsg.fields_name, ubxmsg.values))
                    self.data.emit(val)

        elif lst[0] == 'ADC':
            val = copy.copy(lst[1])
            self.data.emit(val)

        elif lst[0] == 'INC':
            val = copy.copy(lst[1])
            ang_x, ang_y = struct.unpack('>ll', val)
            ang = [ang_x, ang_y]
            self.data.emit(ang)