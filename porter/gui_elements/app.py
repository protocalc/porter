from PyQt5 import QtWidgets, QtCore
import copy

from gui_elements.tabs.control import ControlTab
from gui_elements.tabs.telemetry import TelemetryTab
from gui_elements.dialogs.xbee import XBEE_params
from gui_elements.dialogs.ublox import UBLOX_params

class MainWindow(QtWidgets.QMainWindow):

    xbee_comms = QtCore.pyqtSignal(object)
    local_ublox_object = QtCore.pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.title = 'Porter Control'

        self.setWindowTitle(self.title)

        menubar = self.menuBar()

        self.xbeedata = menubar.addMenu('XBEE Connection')
        xbee_cfg = QtWidgets.QAction('Configuration', self)
        self.xbeedata.addAction(xbee_cfg)
        xbee_cfg.triggered.connect(self.xbee_cfg_menu)

        self.ubloxdata = menubar.addMenu('UBLOX Connection')
        ublox_cfg = QtWidgets.QAction('Configuration', self)
        self.ubloxdata.addAction(ublox_cfg)
        ublox_cfg.triggered.connect(self.ublox_cfg_menu)

        self.TabLayout = MainWindowTab()

        self.xbee_comms.connect(self.TabLayout.tab1.get_xbee_connection)
        self.local_ublox_object.connect(self.TabLayout.tab1.get_ublox_connection)

        self.xbee_comms.connect(self.TabLayout.tab2.get_xbee_connection)
        self.local_ublox_object.connect(self.TabLayout.tab2.get_ublox_connection)

        self.setCentralWidget(self.TabLayout)

    def xbee_cfg_menu(self):

        dialog = XBEE_params()
        dialog.xbee_obj.connect(self.get_xbee_obj)
        dialog.exec_()

        self.xbee_comms.emit(self.xbee_obj)

    @QtCore.pyqtSlot(object)
    def get_xbee_obj(self, obj):
        self.xbee_obj = copy.copy(obj)

    def ublox_cfg_menu(self):

        dialog = UBLOX_params()
        dialog.ubx_obj.connect(self.get_ubx_obj)
        dialog.exec_()

        self.local_ublox_object.emit(self.ubx_obj)

    @QtCore.pyqtSlot(object)
    def get_ubx_obj(self, obj):
        self.ubx_obj = copy.copy(obj)

class MainWindowTab(QtWidgets.QTabWidget):

    '''
    Layout for the main tab window
    '''

    def __init__(self, xbee_connection=None, parent = None):
        super(MainWindowTab, self).__init__(parent)

        self.tab1 = ControlTab()
        self.tab2 = TelemetryTab()

        self.addTab(self.tab1,"Controls")
        self.addTab(self.tab2,"Telemetry")
