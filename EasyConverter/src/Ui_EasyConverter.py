# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'G:\MyProgram\easyworld\EasyConverter\src\EasyConverter.py'
#
# Created: Sun Jan 09 13:02:39 2011
#      by: PyQt4 UI code generator 4.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(405, 418)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(40, 370, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(20, 20, 351, 61))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.plainTextEdit = QtGui.QPlainTextEdit(self.groupBox)
        self.plainTextEdit.setGeometry(QtCore.QRect(20, 20, 261, 31))
        self.plainTextEdit.setObjectName(_fromUtf8("plainTextEdit"))
        self.pushButton = QtGui.QPushButton(self.groupBox)
        self.pushButton.setGeometry(QtCore.QRect(300, 20, 31, 31))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        self.groupBox_2.setGeometry(QtCore.QRect(20, 100, 351, 61))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.plainTextEdit_2 = QtGui.QPlainTextEdit(self.groupBox_2)
        self.plainTextEdit_2.setGeometry(QtCore.QRect(20, 20, 261, 31))
        self.plainTextEdit_2.setObjectName(_fromUtf8("plainTextEdit_2"))
        self.pushButton_2 = QtGui.QPushButton(self.groupBox_2)
        self.pushButton_2.setGeometry(QtCore.QRect(300, 20, 31, 31))
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.groupBox_3 = QtGui.QGroupBox(Dialog)
        self.groupBox_3.setGeometry(QtCore.QRect(20, 180, 351, 111))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.radioButtonMp4 = QtGui.QRadioButton(self.groupBox_3)
        self.radioButtonMp4.setGeometry(QtCore.QRect(10, 20, 89, 16))
        self.radioButtonMp4.setObjectName(_fromUtf8("radioButtonMp4"))
        self.radioButtonFlv = QtGui.QRadioButton(self.groupBox_3)
        self.radioButtonFlv.setGeometry(QtCore.QRect(160, 20, 89, 16))
        self.radioButtonFlv.setObjectName(_fromUtf8("radioButtonFlv"))
        self.radioButtonAvi = QtGui.QRadioButton(self.groupBox_3)
        self.radioButtonAvi.setGeometry(QtCore.QRect(10, 40, 89, 16))
        self.radioButtonAvi.setObjectName(_fromUtf8("radioButtonAvi"))
        self.radioButton3gp = QtGui.QRadioButton(self.groupBox_3)
        self.radioButton3gp.setGeometry(QtCore.QRect(160, 40, 89, 16))
        self.radioButton3gp.setObjectName(_fromUtf8("radioButton3gp"))
        self.progressBar = QtGui.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(20, 330, 351, 23))
        self.progressBar.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.progressBar.setProperty(_fromUtf8("value"), 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "转换源文件", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Dialog", "输出到目录", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("Dialog", "输出文件格式", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonMp4.setText(QtGui.QApplication.translate("Dialog", "MP4(Iphone)", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonFlv.setText(QtGui.QApplication.translate("Dialog", "FLV（Flash）", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonAvi.setText(QtGui.QApplication.translate("Dialog", "AVI", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton3gp.setText(QtGui.QApplication.translate("Dialog", "3GP", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

