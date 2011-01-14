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
        self.config.load()
    
        self.localdirs = self.config.data['monitor_dir']
        self.lm = QStringListModel (self.localdirs )
        
        self.listViewPath.setModel(self.lm)
        
        self.createActions()
        self.createTrayIcon()
        
        self.trayIcon.show()
        
        self.timer = QTimer(self)
        self.connect(self.timer, SIGNAL("timeout()"), self.onTimer)
        self.timer.start(5 * 60 * 1000)
    
    def onTimer(self):
        self.updateRepo()
        
    def updateRepo(self):
        for dir in self.localdirs:
                repo = RepoInfo(unicode(dir))
                worker = SvnWorker(repo)
                print worker.getCurrLocalRevNo()
                print worker.getCurrRepoRevNo()
               
                
    def createActions(self):
        self.configAction = QAction(u"更新设置", self, triggered=self.showNormal)
        self.updateAction = QAction(u"手动更新", self, triggered=self.updateRepo)
        self.quitAction   = QAction(u"结束退出", self, triggered=qApp.quit)

    def createTrayIcon(self):
        icon = QIcon(':/images/trash.svg')
        self.setWindowIcon(icon)

        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(icon)
        
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(self.updateAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.configAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)

        self.trayIcon.setContextMenu(self.trayIconMenu)
    
    @pyqtSignature("")
    def on_btnClose_clicked(self):
        self.config.save()
        self.hide()

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
