from PyQt5 import QtWidgets, QtCore
import copy
import time
import pyqtgraph as pg

class TelemetryTab(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(QtWidgets.QWidget, self).__init__(parent)

        self.plt_thread = 0
        self.data = []
        self.time = []

        self.gps_group()
        self.plotting_group()

        mainlayout = QtWidgets.QGridLayout(self)
        mainlayout.addWidget(self.GPSgroup, 0, 0, 1, 1)
        mainlayout.addWidget(self.PLOTgroup, 0, 1, 1, 1)

        self.setLayout(mainlayout)

    @QtCore.pyqtSlot(object)
    def get_xbee_connection(self, obj):
        self.xbee_connection = copy.copy(obj)
        
    @QtCore.pyqtSlot(object)
    def get_ublox_connection(self, obj):
        self.ublox_local_connection = copy.copy(obj)

    @QtCore.pyqtSlot()
    def get_remote_msg(self, obj):
        self.remote_msg = copy.copy(obj)

        if isinstance(self.remote_msg, dict):
            self.lon.setText(self.remote_msg['lon'])
            self.lat.setText(self.remote_msg['lat'])

        elif isinstance(self.remote_msg, float):
            t = time.time()
            self.update_plot_data(t, self.remote_msg)
        
        elif isinstance(self.remote_msg, list):
            self.angle_x.setText(self.remote_msg[0])
            self.angle_y.setText(self.remote_msg[1])

    
    def update_plot_data(self, t, val):
        self.data.append(val)
        self.time.append(t)

        self.plot.setData(self.time-self.time[0], self.data)


    def gps_group(self):

        self.GPSgroup = QtWidgets.QGroupBox("UBLOX Controls")

        layout = QtWidgets.QGridLayout()

        self.lat_label = QtWidgets.QLabel("Latitude (deg):")
        self.lat = QtWidgets.QLineEdit()

        self.lon_label = QtWidgets.QLabel("Longitude (deg):")
        self.lon = QtWidgets.QLineEdit()

        self.altitude_label = QtWidgets.QLabel("Altitude (m): ")
        self.altitude = QtWidgets.QLineEdit()

        self.angle_x_label = QtWidgets.QLabel("Drone Angle X (deg): ")
        self.angle_x = QtWidgets.QLineEdit()

        self.angle_y_label = QtWidgets.QLabel("Drone Angle Y (deg): ")
        self.angle_y = QtWidgets.QLineEdit()

        self.azimuth_label = QtWidgets.QLabel("Azimuth (deg) :")
        self.elevation_label = QtWidgets.QLabel("Elevation (deg) :")

        layout.addWidget(self.lat_label, 0, 0, 1, 1)
        layout.addWidget(self.lat, 0, 1, 1, 1)
        layout.addWidget(self.lon_label, 1, 0, 1, 1)
        layout.addWidget(self.lon, 1, 1, 1, 1)
        layout.addWidget(self.angle_x_label, 2, 0, 1, 1)
        layout.addWidget(self.angle_x, 2, 1, 1, 1)
        layout.addWidget(self.angle_y_label, 3, 0, 1, 1)
        layout.addWidget(self.angle_y, 3, 1, 1, 1)

        self.GPSgroup.setLayout(layout)

    def plotting_group(self):

        self.guiplot = pg.PlotWidget()
        self.plot = self.guiplot.plot()
        self.plot.setClipToView(True)

        self.PLOTgroup = QtWidgets.QGroupBox("Power Emitted")

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.guiplot)

        #self.adc_plot()

        self.PLOTgroup.setLayout(layout)