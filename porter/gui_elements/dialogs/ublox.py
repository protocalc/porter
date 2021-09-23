from PyQt5 import QtWidgets, QtCore
import ublox.ublox as ublox

class UBLOX_params(QtWidgets.QDialog):

    ubx_obj = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(QtWidgets.QDialog, self).__init__(parent)

        self.setWindowTitle('Ublox Connections Parameters')

        self.ublox_local_add_label = QtWidgets.QLabel('Ublox Local Serial Port : ')
        self.ublox_local_add = QtWidgets.QLineEdit('')

        self.ublox_local_baud_label = QtWidgets.QLabel('Ublox Local Serial Baudrate : ')
        self.ublox_local_baud = QtWidgets.QComboBox()

        available_baudrates = ['200', '2400', '4800', '9600', '14400', '19200', '38400', '57600', \
                               '115200', '230400', '460800', '921600']
        self.ublox_local_baud.addItems(available_baudrates)

        self.connect_ublox = QtWidgets.QPushButton('Connect Local Ublox')

        layout = QtWidgets.QGridLayout()

        layout.addWidget(self.ublox_local_add_label, 0, 0)
        layout.addWidget(self.ublox_local_add, 0, 1)
        layout.addWidget(self.ublox_local_baud_label, 1, 0)
        layout.addWidget(self.ublox_local_baud, 1, 1)
        layout.addWidget(self.connect_ublox, 2, 1)

        self.connect_ublox.clicked.connect(self.connect_local_ublox)

        self.setLayout(layout)

    def connect_local_ublox(self):

        ubx = ublox.UBXio(self.ublox_local_add.text().strip(), \
                          int(self.ublox_local_baud.currentText()))

        self.ubx_obj.emit(ubx.conn)