# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'G:\MyProgram\easyworld\EasySvn\src\DlgConfig.ui'
#
# Created: Fri Jan 14 15:07:16 2011
#      by: PyQt4 UI code generator 4.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_DlgConfig(object):
    def setupUi(self, DlgConfig):
        DlgConfig.setObjectName(_fromUtf8("DlgConfig"))
        DlgConfig.resize(470, 308)
        self.btnClose = QtGui.QPushButton(DlgConfig)
        self.btnClose.setGeometry(QtCore.QRect(370, 270, 75, 23))
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.btnDelete = QtGui.QPushButton(DlgConfig)
        self.btnDelete.setGeometry(QtCore.QRect(280, 270, 75, 23))
        self.btnDelete.setObjectName(_fromUtf8("btnDelete"))
        self.BtnAdd = QtGui.QPushButton(DlgConfig)
        self.BtnAdd.setGeometry(QtCore.QRect(190, 270, 75, 23))
        self.BtnAdd.setObjectName(_fromUtf8("BtnAdd"))
        self.label = QtGui.QLabel(DlgConfig)
        self.label.setGeometry(QtCore.QRect(20, 10, 151, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.listViewPath = QtGui.QListView(DlgConfig)
        self.listViewPath.setGeometry(QtCore.QRect(20, 30, 431, 231))
        self.listViewPath.setObjectName(_fromUtf8("listViewPath"))

        self.retranslateUi(DlgConfig)
        QtCore.QMetaObject.connectSlotsByName(DlgConfig)

    def retranslateUi(self, DlgConfig):
        DlgConfig.setWindowTitle(QtGui.QApplication.translate("DlgConfig", "设置", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("DlgConfig", "完成", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDelete.setText(QtGui.QApplication.translate("DlgConfig", "删除", None, QtGui.QApplication.UnicodeUTF8))
        self.BtnAdd.setText(QtGui.QApplication.translate("DlgConfig", "添加", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("DlgConfig", "需要定时更新的本地路径", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    DlgConfig = QtGui.QDialog()
    ui = Ui_DlgConfig()
    ui.setupUi(DlgConfig)
    DlgConfig.show()
    sys.exit(app.exec_())

