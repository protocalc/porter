from PyQt5 import QtCore, QtWidgets

import gui_elements.app as mainwindow
from gui_elements.threads.receiver import *
from gui_elements.threads.datahandler import *
import sys

def main():
    app = QtWidgets.QApplication(sys.argv)

    ex = mainwindow.MainWindow()

    receiver_thread = QtCore.QThread()
    receiver_worker = receiveworker()

    receiver_worker.moveToThread(receiver_thread)

    datahandler_thread = QtCore.QThread()
    datahandler_worker = datahandler()

    datahandler_worker.moveToThread(datahandler_thread)
    
    ### CONNECTION ###
    ex.xbee_comms.connect(receiver_worker.get_xbee_connection) #Pass the XBEE info to the receiver thread
    receiver_worker.data.connect(datahandler_worker.handler)   #Pass the received data to the handler 
    datahandler_worker.data.connect(ex.TabLayout.tab2.get_remote_msg) #Pass the data to the telemetry tab to plot it and show it 
    
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()