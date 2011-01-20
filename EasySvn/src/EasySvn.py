#-*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui
from Main import  *

from config import *

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    QtGui.QApplication.setQuitOnLastWindowClosed(False)
    config = Config("EasySvn.cfg")
    dlg = MainWindow(config)
    #window.show()
    sys.exit(app.exec_())
    
