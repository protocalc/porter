from PyQt5 import QtCore
import copy

class receiveworker(QtCore.QObject):

    data = QtCore.pyqtSignal(list)
    finished = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        self._running = True

    def run(self):

        self.data = [None, None]

    @QtCore.pyqtSlot(object)
    def get_xbee_connection(self, obj):
        self.xbee_connection = copy.copy(obj)

        while self._running:
            dest, msg = self.xbee_connection.poll_msg()
            self.data[0] = dest
            self.data[1] = msg

            self.data.emit()
            self.finished.emit()

    def stop(self):
        self._running = False