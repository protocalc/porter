from PyQt5 import QtCore
import ublox.ublox as ublox

class cmdworker_remote(QtCore.QObject):

    finished = QtCore.pyqtSignal()

    def __init__(self, tx_queue, xbee_connection, parent=None):
        super().__init__()
        self.queue = tx_queue
        self.xbee_connection = xbee_connection

        self._running = True

    def run(self):

        while self._running:
            while not self.queue.empty():
                msg = self.queue.get()
                if msg[0] == 'UBX':
                    ubxmsg = ublox.UBXMessage(msg_class='CFG', msg_id='VALSET')
                    ubxmsg.encode(msg[1])
                    msg = b'UBX'+ubxmsg.ubx_msg+b'END'
                elif msg[0] == 'ADC':
                    msg = b'ADC'+bytes(msg[-1])+b'END'
                self.xbee_connection.send_msg(msg)
            
            self.finished.emit()

    def stop(self):
        self._running = False