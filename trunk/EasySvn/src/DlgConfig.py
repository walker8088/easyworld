# -*- coding: utf-8 -*-

"""
Module implementing DlgConfig.
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from Ui_DlgConfig import Ui_DlgConfig

from SvnWorker import *

import systray_rc

class DlgConfig(QDialog, Ui_DlgConfig):
    """
    Class documentation goes here.
    """
    def __init__(self, config,  parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.config = config
        
        self.localdirs = self.config.data['monitor_dir']
        self.lm = QStringListModel (self.localdirs )
        
        self.listViewPath.setModel(self.lm)
        
    @pyqtSignature("")
    def on_btnClose_clicked(self):
        self.config.save()
        self.close()

    @pyqtSignature("")
    def on_btnDelete_clicked(self):
        row = self.listViewPath.currentIndex().row()
        if row < 0 : return
        del self.localdirs[row]
        self.lm.setStringList(QStringList(self.localdirs))
        
    @pyqtSignature("")
    def on_BtnAdd_clicked(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self, u"选择需要监控的目录", "",  options)
        if directory:
            self.localdirs.append(directory)
            self.lm.setStringList(QStringList(self.localdirs))
