from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSignalMapper, QSize, QTextStream, Qt)
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QMdiArea, QMessageBox, QTextEdit, QWidget)
from PyQt5 import QtCore, QtGui, uic
from utils import get_project_root


ROOT_PATH = str(get_project_root())

class MdiChildNewProduct(QWidget):

    def __init__(self):
        super(QWidget, self).__init__()
        self.ui = uic.loadUi(ROOT_PATH + "/layouts/newproduct.ui", self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.isUntitled = True
        #self.setMinimumSize(400, 200)
        self.connectEvents();

    def connectEvents(self):
        self.pushButton.clicked.connect(self.onPushButton_click)

    def onPushButton_click(self):
        QMessageBox.warning(self, "MDI", "SOY PUSH BUTTON")
