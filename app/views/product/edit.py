import logging
from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSignalMapper, QSize, QTextStream, Qt, pyqtSlot, QModelIndex, QRegExp)
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QMdiArea, QMessageBox, QTextEdit, QDialog, QWidget, QTableView)
from PyQt5.QtGui import QRegExpValidator
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from db.DBManager import DBManager
from db.models.objects import Product
from db.models.alchemicaltablemodel import AlchemicalTableModel
from decimal import Decimal
from pprint import pprint
from utils import get_project_root


ROOT_PATH = str(get_project_root())

class ProductoEditView(QDialog):
    def __init__(self, codbar):
        super(QDialog, self).__init__()
        self.ui = uic.loadUi(ROOT_PATH + "/layouts/product/edit.ui", self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.isUntitled = True
        self.txt_codbarra.setText(codbar)
        self.txt_nombre.setFocus()
        # self.setMinimumSize(400, 200)
        self.connectEvents()
        self.dbm = DBManager()

    def __del__(self):
        print ("Object destroyed");

    def connectEvents(self):
        self.pb_cancelar.clicked.connect(lambda:self.close())
        self.pb_guardar.clicked.connect(lambda:self.guardarProducto())
        reg_ex_int = QRegExp("[0-9]+.?[0-9]")
        reg_ex_dec = QRegExp("[0-9]+.?[0-9]{,2}")
        reg_ex_dec = QRegExp("[0-9]+.?[0-9]{,2}")
        self.txt_codbarra.setValidator(QRegExpValidator(reg_ex_int, self.txt_codbarra))
        self.txt_precio_venta.setValidator(QRegExpValidator(reg_ex_dec, self.txt_precio_venta))
        self.txt_iva.setValidator(QRegExpValidator(reg_ex_dec, self.txt_iva))

    def guardarProducto(self):
        if (len(self.txt_codbarra.text())==0):
            QMessageBox.information(None, "Nuevo Producto", "Debe ingresar un código de barras")
            return

        if (len(self.txt_nombre.text())==0):
            QMessageBox.information(None, "Nuevo Producto", "Debe ingresar un nombre")
            return

        if (len(self.txt_iva.text())==0):
            QMessageBox.information(None, "Nuevo Producto", "Debe ingresar un valor para IVA")
            return

        if (len(self.txt_precio_venta.text())==0):
            QMessageBox.information(None, "Nuevo Producto", "Debe ingresar un Precio de Venta")
            return

        self.txt_iva.setText(self.txt_iva.text().replace(',','.'))
        fIVA = float(self.txt_iva.text())
        if ( fIVA < 0 or fIVA > 100):
            QMessageBox.information(None, "Nuevo Producto", "IVA debe ser un número entre 0 y 100")
            return

        self.txt_precio_venta.setText(self.txt_precio_venta.text().replace(',','.'))
        pVenta = float(self.txt_precio_venta.text())
        if (pVenta < 0):
            QMessageBox.information(None, "Nuevo Producto", "Debe ingresar un precio de venta mayor o igual que cero")
            return

        prod = Product(
            codbarra=self.txt_codbarra.text(),
            nombre=self.txt_nombre.text(),
            precio_venta=self.txt_precio_venta.text(),
            iva=self.txt_iva.text(),
            enabled=True
        )
        self.dbm.session.add(prod)
        self.dbm.session.commit()
        self.close()
