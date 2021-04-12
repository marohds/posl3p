import logging
from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSignalMapper, QSize, QTextStream, Qt)
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QMdiArea, QMessageBox, QTextEdit, QWidget)
from PyQt5 import QtCore, QtGui, uic
from db.DBManager import DBManager
from utils import get_project_root

ROOT_PATH = str(get_project_root())

class DbManagerView(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        self.ui = uic.loadUi(ROOT_PATH + "/layouts/db_manager.ui", self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.isUntitled = True
        #self.setMinimumSize(400, 200)
        self.connectEvents()
        self.dbm = DBManager()

    def __del__(self):
        pass

    def connectEvents(self):
        self.pb_loadProducts.clicked.connect(self.loadProducts)
        self.pb_crearDB.clicked.connect(self.create_database)

    def create_database(self):
        self.dbm.create_database()
        logging.info("DB Manager - Base creada!")

    def loadProducts(self):
        self.dbm.build_products()
        logging.info("DB Manager - Productos cargados!")
