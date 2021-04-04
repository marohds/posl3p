import sys
import logging
import logging.handlers
import os
import datetime as dt
import mdi_rc
import sqlalchemy.sql.default_comparator # Necesario para compilar exe
from PyQt5 import QtCore, QtGui, uic
from PyQt5.Qt import PYQT_VERSION_STR
from sip import SIP_VERSION_STR
from PyQt5.QtCore import (QT_VERSION_STR, QFile, QFileInfo, QPoint, QSettings, QSignalMapper, QSize, QTextStream, Qt)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QMdiArea, QMessageBox, QTextEdit, QWidget)
from views.product.new import MdiChildNewProduct
from views.venta.vender import MdiChildVender
from views.venta.index import VentaIndexView
from views.cierre.index import CierreIndexView
from views.DbManagerView import DbManagerView
from views.product.index import ProductoIndexView
from utils import get_project_root


global ROOT_PATH

class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.ui = uic.loadUi(ROOT_PATH + "/layouts/mainwindow.ui", self)
        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdiArea)
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)
        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        #self.updateMenus()
        #self.readSettings()
        #self.setWindowTitle("MDI")

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_F1:
            self.vender.trigger()
            return
        if key == QtCore.Qt.Key_F2:
            self.indexProd.trigger()
            return
        super(MainWindow, self).keyPressEvent(event)

    def ShowControlPanel(self):
            self.ControlPanel = Control_panel_window(self)
            self.ControlPanel.setWindowFlags(QtCore.Qt.Window)
            self.ControlPanel.show()

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)

    def activeMdiChild(self, childname):
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            if activeSubWindow.widget().objectName() == childname:
                return activeSubWindow.widget()
        return None

    def createMdiVenderChild(self):
        child = MdiChildVender(self)
        child.setObjectName("venderchild")
        child.resize(687, 438)
        self.mdiArea.addSubWindow(child)
        return child

    def vender(self):
        try:
            child = self.venderChild
            child.showMaximized()
            child.txt_codbar.setFocus()
        except (RuntimeError, AttributeError):
            child = self.createMdiVenderChild()
            self.venderChild = child
            child.showMaximized()

    def createMdiDBManager(self):
        child = DbManagerView()
        child.setObjectName("dbmanagerchild")
        child.resize(687, 438)
        self.mdiArea.addSubWindow(child)
        return child

    def openDbManager(self):
        try:
            child = self.dbManagerChild
            child.showMaximized()
        except (RuntimeError, AttributeError):
            child = self.createMdiDBManager()
            self.dbManagerChild = child
            child.showMaximized()

    def createMdiProductIndex(self):
        child = ProductoIndexView(self)
        child.setObjectName("productindexchild")
        child.resize(687, 438)
        self.mdiArea.addSubWindow(child)
        return child

    def indexProduct(self):
        try:
            child = self.productIndexChild
            child.showMaximized()
            child.txt_buscar.setFocus()
        except (RuntimeError, AttributeError):
            child = self.createMdiProductIndex()
            self.productIndexChild = child
            child.showMaximized()

    def createMdiVentaIndex(self):
        child = VentaIndexView(self)
        child.setObjectName("ventaindexchild")
        child.resize(687, 438)
        self.mdiArea.addSubWindow(child)
        return child

    def indexVenta(self):
        try:
            child = self.ventaIndexChild
            child.showMaximized()
        except (RuntimeError, AttributeError):
            child = self.createMdiVentaIndex()
            self.ventaIndexChild = child
            child.showMaximized()

    def createMdiCierreIndex(self):
        child = CierreIndexView(self)
        child.setObjectName("cierreindexchild")
        child.resize(687, 438)
        self.mdiArea.addSubWindow(child)
        return child

    def indexCierres(self):
        try:
            child = self.cierreIndexChild
            child.showMaximized()
        except (RuntimeError, AttributeError):
            child = self.createMdiCierreIndex()
            self.cierreIndexChild = child
            child.showMaximized()

    def createActions(self):
        self.vender = QAction(QIcon(':/images/cart2.png'), "&Vender", self,
                shortcut=QKeySequence.New, statusTip="Abrir ventana para Venta",
                triggered=self.vender)
        self.indexProd = QAction(QIcon(':/images/products.png'), "&Productos", self,
                shortcut=QKeySequence.New, statusTip="Maestro de Productos",
                triggered=self.indexProduct)
        self.indexVta = QAction(QIcon(':/images/ventas.png'), "&Consulta de Ventas", self,
                shortcut=QKeySequence.New, statusTip="Consulta de Ventas",
                triggered=self.indexVenta)
        self.dbManager = QAction(QIcon(':/images/sell.png'), "DB &Manager", self,
                shortcut=QKeySequence.New, statusTip="Administración de Base de Datos",
                triggered=self.openDbManager)
        self.indexZ = QAction(QIcon(':/images/cierre.png'), "&Cierres", self,
                shortcut=QKeySequence.New, statusTip="Cierres Diario",
                triggered=self.indexCierres)

    def createMenus(self):
        pass
#        self.fileMenu = self.menuBar().addMenu("&File")
#        self.fileMenu.addAction(self.dbManager)
#        self.fileMenu = self.menuBar().addMenu("&Productos")
#        self.fileMenu.addAction(self.indexProd)
#        self.fileMenu = self.menuBar().addMenu("&Consulta de Ventas")
#        self.fileMenu.addAction(self.indexVta)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.vender)
        self.fileToolBar = self.addToolBar("Productos")
        self.fileToolBar.addAction(self.indexProd)
        self.fileToolBar = self.addToolBar("Consulta Ventas")
        self.fileToolBar.addAction(self.indexVta)
        self.fileToolBar = self.addToolBar("Cierres")
        self.fileToolBar.addAction(self.indexZ)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def showKeymaps(self):
        # F1 -> Vender
        # F2 -> Maestro de Productos
        # En la ventana Vender
        #   V -> Agregar monto Varios
        #   C -> Agregar monto Carnicería
        #   F -> Agregar monto Fiambres
        #   Q -> Agregar monto Quitar Unidad
        #   P -> Registro Pago
        #   T -> Imprimir Ticket
        #   K -> Finalizar Venta
        #   A -> Anular Venta
        #   N -> NUEVA Venta
        pass

if __name__ == "__main__":

    ROOT_PATH = str(get_project_root())
    print("Qt version:", QT_VERSION_STR)
    print("SIP version:", SIP_VERSION_STR)
    print("PyQt version:", PYQT_VERSION_STR)
    print("ROOT_PATH:", ROOT_PATH)

    __log_folder_name = "logs/"
    __log_file_name = "{}-{}_log_file.txt".format("pos", dt.datetime.utcnow().isoformat().replace(":", "-"))
    __log_format = '%(asctime)s - %(name)-30s - %(levelname)s - %(message)s'
    __console_date_format = '%Y-%m-%d %H:%M:%S'
    __file_date_format = '%Y-%m-%d %H-%M-%S'

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    console_formatter = logging.Formatter(__log_format, __console_date_format)

    file_formatter = logging.Formatter(__log_format, __file_date_format)
    file_handler = logging.FileHandler(__log_folder_name + __log_file_name, mode='a', delay=True)
    # file_handler = TqdmLoggingHandler2(__log_file_name, mode='a', delay=True)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    root.addHandler(file_handler)

    app = QApplication(sys.argv)

    window = MainWindow()
    #window.show()
    window.showMaximized()
    try:
        sys.exit(app.exec_())
        # exit(main())
    except Exception:
        logging.exception("Exception in main()")
        exit(1)

    # app.exec_()
    #
