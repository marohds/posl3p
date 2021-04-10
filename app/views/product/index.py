import logging
from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSignalMapper, QSize, QTextStream, Qt, pyqtSlot, QModelIndex)
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QMdiArea, QMessageBox, QTextEdit, QWidget, QTableView)
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import QFont
from db.DBManager import DBManager
from db.models.objects import Product
from db.models.alchemicaltablemodel import AlchemicalTableModel
from views.product.edit import ProductoEditView
from pprint import pprint
from utils import get_project_root


ROOT_PATH = str(get_project_root())

class ProductoIndexView(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(QWidget, self).__init__()
        self.ui = uic.loadUi(ROOT_PATH + "/layouts/product/index.ui", self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.model = None
        self.isUntitled = True
        # self.setMinimumSize(400, 200)
        self.editMode = False
        self.connectEvents()
        self.dbm = DBManager()
        self.btnCancelarCambios.hide()
        self.btnGuardarCambios.hide()
        self.btn_editMode.hide()
        self.session = self.dbm.getNewSession()
        fnt = QFont("Arial", 18)
        self.tv_productos.setFont(fnt)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_F1:
            self.parent.vender.trigger()
        if key == QtCore.Qt.Key_F2:
            self.parent.indexProd.trigger()

    def __del__(self):
        try:
            if self.session.dirty:
                self.session.rollback()
            self.session.close()
        except:
            pass

    def connectEvents(self):
        self.pb_buscar.clicked.connect(self.searchProduct)
        self.pb_buscarNombre.clicked.connect(self.searchProducts)
        self.txt_buscar.returnPressed.connect(self.pb_buscar.click)
        self.pb_nuevo.clicked.connect(self.openNewProduct)
        self.btn_editMode.clicked.connect(self.setEditModeTrue)
        self.btnCancelarCambios.clicked.connect(self.cancelarCambios)
        self.btnGuardarCambios.clicked.connect(self.guardarCambios)

    def openNewProduct(self):
        if self.session.dirty:
            QMessageBox.information(None, "Cambios pendientes", "Tiene cambios pendientes sin guardar")
            return None
        self.setEditMode(False)
        modal = ProductoEditView(None)
        modal.setObjectName("productedit")
        modal.resize(687, 438)
        modal.exec_()

    def setEditModeTrue(self):
        self.setEditMode(True)

    def setEditModeFalse(self):
        self.setEditMode(False)

    def setEditMode(self, value):
        if (self.model == None) :
            return None
        if value == True :
            self.editMode = value
            self.btn_editMode.hide()
            self.btnCancelarCambios.show()
            self.btnGuardarCambios.show()
        else :
            self.editMode = value
            self.btn_editMode.show()
            self.btnCancelarCambios.hide()
            self.btnGuardarCambios.hide()
        self.refreshTable()

    def guardarCambios(self):
        self.session.commit()
        self.setEditMode(False)

    def cancelarCambios(self):
        self.session.rollback()
        self.setEditMode(False)

    def searchProduct(self):
        txtBuscar = self.txt_buscar.text()
        self.productsQuery = self.session.query(Product).filter_by(codbarra=txtBuscar)
        self.refreshTable()

    def searchProducts(self):
        txtBuscar = self.txt_buscar.text()
        self.productsQuery = self.session.query(Product).filter(Product.nombre.like('%' + txtBuscar + '%'))
        self.refreshTable()

    def refreshTable(self):
        self.model = AlchemicalTableModel(
            self.session, #FIXME pass in sqlalchemy session object
            self.productsQuery, #sql alchemy mapped object
            None,
            [Qt.AscendingOrder,2], # orderby
            [
              ('Producto', Product.id, 'id', {'editable': False}),
              ('Cod. Barra', Product.codbarra, 'codbarra', {'editable': self.editMode}),
              ('Nombre', Product.nombre, 'nombre', {'editable': self.editMode}),
              ('Precio Venta', Product.precio_venta, 'precio_venta', {'editable': self.editMode}),
              ('% IVA', Product.iva, 'iva', {'editable': self.editMode}),
            ])
        self.tv_productos.setModel(self.model.refresh())
        self.lblCount.setText("Total = " + str(self.model.rowCount(None)))
        self.btn_editMode.show() if (self.model.rowCount(None) >= 1) else self.btn_editMode.hide()
        header = self.tv_productos.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setStyleSheet("QHeaderView { font-size: 18pt; font-weight: bold }")
