from PyQt5 import QtWidgets, QtCore
import telemetry.xbee as xbee

class XBEE_params(QtWidgets.QDialog):

    xbee_obj = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(QtWidgets.QDialog, self).__init__(parent)

        self.setWindowTitle('XBEE Connections Parameters')

        self.xbee_local_add_label = QtWidgets.QLabel('XBee Local Serial Port : ')
        self.xbee_local_add = QtWidgets.QLineEdit('')

        self.xbee_local_baud_label = QtWidgets.QLabel('XBee Local Serial Baudrate : ')
        self.xbee_local_baud = QtWidgets.QComboBox()

        available_baudrates = ['1200', '2400', '4800', '9600', '14400', '19200', '38400', '57600', \
                               '115200', '230400', '460800', '921600']
        self.xbee_local_baud.addItems(available_baudrates)

        self.xbee_remote_id_label = QtWidgets.QLabel('XBee Remote ID :')
        self.xbee_remote_id = QtWidgets.QLineEdit('')

        self.connect_xbee_btn = QtWidgets.QPushButton('Write XBee Configuration')

        layout = QtWidgets.QGridLayout()

        layout.addWidget(self.xbee_local_add_label, 0, 0)
        layout.addWidget(self.xbee_local_add, 0, 1)
        layout.addWidget(self.xbee_local_baud_label, 1, 0)
        layout.addWidget(self.xbee_local_baud, 1, 1)
        layout.addWidget(self.xbee_remote_id_label, 2, 0)
        layout.addWidget(self.xbee_remote_id, 2, 1)
        layout.addWidget(self.connect_xbee_btn, 3, 1)

        self.connect_xbee_btn.clicked.connect(self.connect_xbee)

        self.setLayout(layout)

    def connect_xbee(self):

        xbee_comms = xbee.comms(self.xbee_local_add, self.xbee_local_baud, \
                                self.xbee_remote_id)

        self.xbee_obj.emit(xbee_comms)