from PyQt5 import QtWidgets, QtCore
import copy
from queue import Queue
import ublox.ubx_cfg_db as db
from gui_elements.threads.cmdremote import *
from gui_elements.threads.cmdlocal import *

class ControlTab(QtWidgets.QWidget):
    
    def __init__(self, parent=None):
        super(QtWidgets.QWidget, self).__init__(parent)

        self.cmd_list = []

        self.rtcm_header = 'RTCM'.encode('utf-8')
        self.rtcm_tail = 'END'.encode('utf-8')
        self.rtcm_flag = True

        self.tx_queue = Queue()
        self.tx_lst = []
        self.local_queue = Queue()
        self.local_lst = []

        self.ubx_group()
        self.adc_group()

        mainlayout = QtWidgets.QGridLayout(self)
        mainlayout.addWidget(self.UBXgroup, 0, 0, 1, 2)
        mainlayout.addWidget(self.ADCgroup, 1, 0, 1, 2)

        self.setLayout(mainlayout)

    @QtCore.pyqtSlot(object)
    def get_xbee_connection(self, obj):
        self.xbee_connection = copy.copy(obj)

    @QtCore.pyqtSlot(object)
    def get_ublox_connection(self, obj):
        self.ublox_local_connection = copy.copy(obj)

    def ubx_group(self):

        self.UBXgroup = QtWidgets.QGroupBox("UBLOX Controls")

        layout = QtWidgets.QGridLayout()

        self.ubx_label = QtWidgets.QLabel("Device :")
        
        self.ubx_device = QtWidgets.QComboBox()
        self.ubx_device.addItem('BASE')
        self.ubx_device.addItem('ROVER')

        self.ubx_cfg_label = QtWidgets.QLabel("Configuration :")

        self.ubx_cfg = QtWidgets.QComboBox()
        self.ubx_cfg.setEditable(True)
        self.ubx_cfg.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion) 
        self.ubx_cfg.setInsertPolicy(QtWidgets.QComboBox.NoInsert)

        cfg_list = list(db.UBX_CONFIG_DATABASE.keys())
        self.ubx_cfg.addItems(cfg_list)

        self.ubx_cfg_value_label = QtWidgets.QLabel("Value :")
        self.ubx_cfg_value = QtWidgets.QLineEdit()

        self.ubx_cfg_transaction_label = QtWidgets.QLabel("Transaction :")
        self.ubx_cfg_transaction = QtWidgets.QCheckBox()

        self.ubx_add_cmd = QtWidgets.QPushButton("Add cfg to queue")

        self.ubx_send_cmd = QtWidgets.QPushButton("Send to UBLOX")

        self.ubx_rtk_cfg_label = QtWidgets.QLabel('Configure RTCM Messages for RTK Measurments')
        self.ubx_rtk_cfg = QtWidgets.QCheckBox()

        self.survey_time_label = QtWidgets.QLabel('Survey Time (s)')
        self.survey_time = QtWidgets.QLineEdit('')

        self.survey_accuracy_label = QtWidgets.QLabel('Survey Accuracy (m)')
        self.survey_accuracy = QtWidgets.QLineEdit('') 
        
        self.send_rtk_cfg = QtWidgets.QPushButton('Send RTK Configuration')

        self.start_rtk_live = QtWidgets.QPushButton('Start RTK Communication')
        self.end_rtk_live = QtWidgets.QPushButton('End RTK Communication')

        layout.addWidget(self.ubx_label, 0, 0, 1, 1)
        layout.addWidget(self.ubx_device, 0, 1, 1, 1)

        layout.addWidget(self.ubx_cfg_label, 1, 0, 1, 1)
        layout.addWidget(self.ubx_cfg, 1, 1, 1, 1)

        layout.addWidget(self.ubx_cfg_value_label, 1, 2, 1, 1)
        layout.addWidget(self.ubx_cfg_value, 1, 3, 1, 1)

        layout.addWidget(self.ubx_cfg_transaction_label, 1, 4, 1, 1)
        layout.addWidget(self.ubx_cfg_transaction, 1, 5, 1, 1)

        layout.addWidget(self.ubx_add_cmd, 1, 6, 1, 1)

        layout.addWidget(self.ubx_send_cmd, 2, 6, 1, 1)

        layout.addWidget(self.ubx_rtk_cfg_label, 3, 0, 1, 1)
        layout.addWidget(self.ubx_rtk_cfg, 3, 1, 1, 1)

        layout.addWidget(self.survey_time_label, 4, 2, 1, 1)
        layout.addWidget(self.survey_time, 4, 3, 1, 1)

        layout.addWidget(self.survey_accuracy_label, 5, 2, 1, 1)
        layout.addWidget(self.survey_accuracy, 5, 3, 1, 1)

        layout.addWidget(self.send_rtk_cfg, 4, 5, 2, 2)

        layout.addWidget(self.start_rtk_live, 6, 5, 1, 1)
        layout.addWidget(self.end_rtk_live, 6, 6, 1, 1)

        if not self.ubx_rtk_cfg.isChecked():
            self.survey_accuracy_label.setVisible(False)
            self.survey_time_label.setVisible(False)
            self.survey_accuracy.setVisible(False)
            self.survey_accuracy.setEnabled(False)
            self.survey_time.setVisible(False)
            self.survey_time.setEnabled(False)
            self.send_rtk_cfg.setVisible(False)
            self.send_rtk_cfg.setEnabled(False)
            self.start_rtk_live.setVisible(False)
            self.start_rtk_live.setEnabled(False)
            self.end_rtk_live.setVisible(False)
            self.end_rtk_live.setEnabled(False)

        self.ubx_add_cmd.clicked.connect(self.create_ubx_queue)
        self.ubx_send_cmd.clicked.connect(self.send_ubx_queue)
        self.ubx_rtk_cfg.toggled.connect(self.rtk_configuration)
        self.ubx_device.activated.connect(self.rtk_configuration)

        self.UBXgroup.setLayout(layout)

    def rtk_configuration(self):

        if self.ubx_rtk_cfg.isChecked():

            if self.ubx_device.currentText().strip() == 'BASE':
                self.survey_accuracy_label.setVisible(True)
                self.survey_time_label.setVisible(True)
                self.survey_accuracy.setVisible(True)
                self.survey_accuracy.setEnabled(True)
                self.survey_time.setVisible(True)
                self.survey_time.setEnabled(True)
                self.start_rtk_live.setVisible(True)
                self.start_rtk_live.setEnabled(True)
                self.end_rtk_live.setVisible(True)
                self.end_rtk_live.setEnabled(True)

            else:
                self.survey_accuracy_label.setVisible(False)
                self.survey_time_label.setVisible(False)
                self.survey_accuracy.setVisible(False)
                self.survey_accuracy.setEnabled(False)
                self.survey_time.setVisible(False)
                self.survey_time.setEnabled(False)
                self.start_rtk_live.setVisible(False)
                self.start_rtk_live.setEnabled(False)
                self.end_rtk_live.setVisible(False)
                self.end_rtk_live.setEnabled(False)

            self.send_rtk_cfg.setVisible(True)
            self.send_rtk_cfg.setEnabled(True)

        else:
            self.survey_accuracy_label.setVisible(False)
            self.survey_time_label.setVisible(False)
            self.survey_accuracy.setVisible(False)
            self.survey_accuracy.setEnabled(False)
            self.survey_time.setVisible(False)
            self.survey_time.setEnabled(False)
            self.send_rtk_cfg.setVisible(False)
            self.send_rtk_cfg.setEnabled(False)
            self.start_rtk_live.setVisible(False)
            self.start_rtk_live.setEnabled(False)
            self.end_rtk_live.setVisible(False)
            self.end_rtk_live.setEnabled(False)

    def create_ubx_queue(self):

        val = int(self.ubx_cfg_value.text())
        self.ubx_cfg_value.clear()

        if self.ubx_device.currentText().strip() == 'BASE':
            self.local_lst.append((self.ubx_cfg.currentText().strip(), val))
        elif self.ubx_device.currentText().strip() == 'ROVER':
            self.tx_lst.append((self.ubx_cfg.currentText().strip(), val))

    def send_ubx_queue(self):

        trans = int(self.ubx_cfg_transaction.isChecked())

        cmd_dict = {
            "version": 0,  
            "layers": {
                'ram': 1,
                'bbr': 0,
                'flash': 0
            },
            "transaction": {
                'action': trans,
            },
            "reserved0": 0
        }
        
        if self.ubx_device.currentText().strip() == 'BASE':
            cmd_dict['group']  = self.local_lst
            self.local_queue.put(['UBX', cmd_dict])
            self.local_lst = []
            self.send_queue_local()
        elif self.ubx_device.currentText().strip() == 'ROVER':
            cmd_dict['group']  = self.tx_lst
            self.tx_queue.put(['UBX', cmd_dict])
            self.tx_lst = []
            self.send_queue_remote()

    def adc_group(self):

        self.ADCgroup = QtWidgets.QGroupBox("ADC Controls")

        layout = QtWidgets.QGridLayout()

        self.gain_label = QtWidgets.QLabel("Gain :")

        self.gain = QtWidgets.QComboBox()

        gain_list = ['2/3', '1', '2', '4', '8']
        self.gain.addItems(gain_list)

        self.gain_cmd = QtWidgets.QPushButton("Send to ADC")


        layout.addWidget(self.gain_label, 0, 0, 1, 1)
        layout.addWidget(self.gain, 0, 1, 1, 1)

        layout.addWidget(self.gain_cmd, 0, 2, 1, 1)

        self.ADCgroup.setLayout(layout)

        self.gain_cmd.clicked.connect(self.send_gain_cmd)
        
    def send_gain_cmd(self):

        self.cmd_list.append(['ADC', self.gain.currentText()])
        self.tx_queue.put(['ADC', 'GAIN', self.gain.currentText()])
        self.send_queue_remote()

    def send_rtk_msg(self):

        msg = self.ublox_base.read_single_msg(msg_cat='rtcm', first_msg=self.rtcm_flag)
        rtcm_msg = (self.rtcm_header+msg+self.rtcm_tail)
        self.tx_queue.put(rtcm_msg)
        self.send_queue_remote()

    def send_queue_local(self):

        self.thread_local = QtCore.QThread()
        self.worker_local = cmdworker_local(self.local_queue, self.ublox_local_connection)
        # Step 4: Move worker to the thread
        self.worker_local.moveToThread(self.thread_local)
        # Step 5: Connect signals and slots
        self.thread_local.started.connect(self.worker_local.run)
        self.worker_local.finished.connect(self.thread_local.quit)
        self.worker_local.finished.connect(self.worker_local.deleteLater)
        self.thread_local.finished.connect(self.thread_local.deleteLater)
        self.worker_local.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread_local.start()

        self.ubx_send_cmd.setEnabled(False)
        self.thread_local.finished.connect(
            lambda: self.ubx_send_cmd.setEnabled(True)
        )

    def send_queue_remote(self):

        self.thread_remote = QtCore.QThread()
        self.worker_remote = cmdworker_remote(self.tx_queue, self.xbee_connection)
        # Step 4: Move worker to the thread
        self.worker_remote.moveToThread(self.thread_remote)
        # Step 5: Connect signals and slots
        self.thread_remote.started.connect(self.worker_remote.run)
        self.worker_remote.finished.connect(self.thread_remote.quit)
        self.worker_remote.finished.connect(self.worker_remote.deleteLater)
        self.thread_remote.finished.connect(self.thread_remote.deleteLater)
        self.worker_remote.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread_remote.start()

    def stop_msg_remote(self):

        self.worker_remote.stop()
        self.thread_remote.exit()
        self.thread_remote.wait()