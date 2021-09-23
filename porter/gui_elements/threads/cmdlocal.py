from PyQt5 import QtCore


class cmdworker_local(QtCore.QObject):

    finished = QtCore.pyqtSignal()

    def __init__(self, local_queue, serial_obj, parent=None):
        super().__init__()
        self.queue = local_queue
        self.serial_obj = serial_obj

        self._running = True

    def run(self):

        while self._running:
            while not self.queue.empty():
                cfg_vals = self.queue.get()
                if cfg_vals[0] == 'UBX':
                    ### Currently support only VALSET values ###
                    self.serial_obj.write_msg('CFG', 'VALSET', cfg_vals[1])
            
            self.finished.emit()

    def stop(self):
        self._running = False