import datetime as dt
import logging
from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSignalMapper, QSize, QTextStream, Qt, QAbstractTableModel)
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QMdiArea, QMessageBox, QLineEdit, QTextEdit, QWidget, QInputDialog)
from PyQt5 import QtCore, QtGui, uic
from db.models.objects import Product, Venta, VentaItem
from db.DBManager import DBManager
from db.models.alchemicaltablemodel import AlchemicalTableModel
from ws.fbwrapper import FBWrapper
from sqlalchemy import desc, func
from decimal import Decimal
from views.product.edit import ProductoEditView
from pprint import pprint
from utils import get_project_root


ROOT_PATH = str(get_project_root())

class MdiChildVender(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(QWidget, self).__init__()
        self.ui = uic.loadUi(ROOT_PATH + "/layouts/venta/vender.ui", self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.isUntitled = True
        self.venta = None
        self.dbm = DBManager()
        self.connectEvents()
        self.session = None
        self.nuevaVenta()
        self.variables = [1,2,3]
        self.selectedProductId = None
        self.selectedPrecioVenta = None
        self.validarCierreZ()
        # self.setMinimumSize(400, 200)

    def validarCierreZ(self):
        f_hoy = dt.datetime(dt.date.today().year, dt.date.today().month, dt.date.today().day,0,0,0)
        countQuery = self.dbm.session.query(func.count(Venta.id).label('ventas')).filter(Venta.estado == 1,Venta.cierre_id == None,Venta.created_at < f_hoy).one()
        if (countQuery[0]>0):
            logging.info("Existen tickets con cierre Z pendiente.")
            QMessageBox.warning(self, "Cierre Z", "Existen tickets con cierre Z pendiente.")

    def __del__(self):
        self.session.rollback()
        self.session.close()
        print ("Object destroyed");

    def keyPressEvent(self, event):
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
        key = event.key()
        if key == QtCore.Qt.Key_F1:
            self.txt_codbar.setText("")
            self.parent.vender.trigger()
            return
        if key == QtCore.Qt.Key_F2:
            self.txt_codbar.setText("")
            self.parent.indexProd.trigger()
            return
        if key == QtCore.Qt.Key_C:
            self.txt_codbar.setText("")
            self.agregarCarniceria()
            return
        if key == QtCore.Qt.Key_V:
            self.txt_codbar.setText("")
            self.agregarVarios()
            return
        if key == QtCore.Qt.Key_F:
            self.txt_codbar.setText("")
            self.agregarFiambre()
            return
        if key == QtCore.Qt.Key_Q:
            self.txt_codbar.setText("")
            self.quitarUnidadItem()
            return
        if key == QtCore.Qt.Key_P:
            self.txt_codbar.setText("")
            self.registrarPago()
            return
        if key == QtCore.Qt.Key_T:
            return
        if key == QtCore.Qt.Key_K:
            self.finalizarVenta(False)
            return
        if key == QtCore.Qt.Key_A:
            return
        if key == QtCore.Qt.Key_N:
            return
        super(MdiChildVender, self).keyPressEvent(event)

    def keyPressTextEditEvent(self, event):
        key = event.key()
        if (key == QtCore.Qt.Key_Return) or (key == QtCore.Qt.Key_Enter):
            self.agregarCodigoBarras()
            return
        self.keyPressEvent(event)
        if ((event.text().isdigit()) or (key == QtCore.Qt.Key_Backspace)):
            QLineEdit.keyPressEvent(self.txt_codbar, event)

    def connectEvents(self):
        self.pb_agregarCodBarras.clicked.connect(self.agregarCodigoBarras)
        self.pb_agregarCarniceria.clicked.connect(self.agregarCarniceria)
        self.pb_agregarFiambre.clicked.connect(self.agregarFiambre)
        self.pb_agregarVarios.clicked.connect(self.agregarVarios)
        self.pb_quitarUltimo.clicked.connect(self.quitarUnidadItem)
        self.pb_ticket.clicked.connect(self.imprimirTicket)
        self.pb_anularVenta.clicked.connect(self.anularVenta)
        self.pb_finalizarVenta.clicked.connect(lambda:self.finalizarVenta(False))
        self.pb_pago.clicked.connect(self.registrarPago)
        self.tb_venta.keyPressEvent = self.keyPressEvent
        self.txt_codbar.keyPressEvent = self.keyPressTextEditEvent
        self.tb_venta.clicked.connect(self.tableVentaClicked)

    def tableVentaClicked(self, clickedIndex):
        model = clickedIndex.model()
        self.selectedProductId = int(model.index(clickedIndex.row(), 0).data())
        self.selectedPrecioVenta = model.index(clickedIndex.row(), 2).data()

    def nuevaVenta(self):
        self.model = None
        self.tb_venta.setModel(None)
        self.venta = Venta()
        self.session = self.dbm.getNewSession()
        self.session.add(self.venta)
        self.curpos = 0
        self.itemCount = 0
        self.setTotalVenta(0,0)
        self.setTotalBultos(0)
        self.setTotalPago(0)
        self.pb_ticket.setDisabled(True)
        self.pb_finalizarVenta.setDisabled(True)
        self.pb_anularVenta.setDisabled(True)
        self.pb_quitarUltimo.setDisabled(True)
        self.pb_pago.setDisabled(True)

    def actualizarPantalla(self):
        self.itemCount = self.venta.items.count()
        self.refreshTable(self.venta.items.all())
        self.pb_ticket.setDisabled((self.itemCount == 0))
        self.pb_finalizarVenta.setDisabled((self.itemCount == 0))
        self.pb_anularVenta.setDisabled((self.itemCount == 0))
        self.pb_quitarUltimo.setDisabled((self.itemCount == 0))
        self.pb_quitarUltimo.setDisabled((self.itemCount == 0))
        self.pb_pago.setDisabled((self.itemCount == 0))
        print('\a')

    def setTotalPago(self, monto):
        self.totalPago = Decimal("%0.2f" % (monto,))
        self.totalVuelto = self.totalPago - self.venta.total_venta
        self.lblTotalPago.setText('<html><head/><body><p><span style=" font-size:48pt;">$ ' + str(self.totalPago) + '</span></p></body></html>')
        self.lblTotalVuelto.setText('<html><head/><body><p><span style=" font-size:48pt;">$ ' + str(self.totalVuelto) + '</span></p></body></html>')

    def setTotalVenta(self, monto, descuento):
        self.venta.total_venta = Decimal("%0.2f" % (monto,))
        self.venta.total_dto = Decimal("%0.2f" % (descuento,))
        self.lblTotalAPagar.setText('<html><head/><body><p><span style=" font-size:48pt;">$ ' + str(self.venta.total_venta) + '</span></p></body></html>')

    def setTotalBultos(self, cant):
        self.totalBultos = cant
        self.lblCantBultos.setText('<html><head/><body><p><span style=" font-size:48pt;">' + str(self.totalBultos) + '</span></p></body></html>')

    def registrarPago(self):
        valor, okPressed = QInputDialog.getDouble(self, "Ingrese un valor", "Value:", 0, 0, 999999999, 2)
        if okPressed:
            if (valor > 0) :
                self.setTotalPago(valor)

    def agregarCodigoBarras(self):
        txtBuscar = self.txt_codbar.text()
        tempSession = self.dbm.getNewSession()
        result = tempSession.query(Product).filter_by(codbarra=txtBuscar).first()
        tempSession.close()
        if (result is not None):
            self.agregarProductoAVenta(result, None, True)
        else:
            logging.info("Producto No Encontrado CodBarra = " + txtBuscar)
            QMessageBox.warning(self, "Venta", "Producto No Encontrado")
            self.openNewProduct()
        self.txt_codbar.setText("")
        self.txt_codbar.setFocus()

    def openNewProduct(self):
        modal = ProductoEditView(self.txt_codbar.text())
        modal.setObjectName("productedit")
        modal.resize(687, 438)
        modal.exec_()

    def agregarVarios(self):
        self.agregarPrecioVariable("1")

    def agregarCarniceria(self):
        self.agregarPrecioVariable("2")

    def agregarFiambre(self):
        self.agregarPrecioVariable("3")

    def quitarUnidadItem(self):
        if (self.selectedProductId is None):
            pass
        else:
            item = self.obtenerItemVenta(self.selectedProductId,self.selectedPrecioVenta)
            if (item.cantidad == 1):
                # item.remove()
                self.session.delete(item)
                self.selectedProductId = None
                self.selectedPrecioVenta = None
            else:
                item.cantidad = item.cantidad - 1
            self.setTotalVenta(self.venta.total_venta - Decimal("%0.2f" % (item.precio_venta,)), self.venta.total_dto - Decimal("%0.2f" % (item.descuento,)))
            self.setTotalBultos(self.totalBultos - 1)
            self.actualizarPantalla()

    def agregarPrecioVariable(self, codProd):
        precio, okPressed = QInputDialog.getDouble(self, "Ingrese un valor", "Value:", 0, 0, 999999999, 2)
        if okPressed:
            if (precio > 0) :
                tempSession = self.dbm.getNewSession()
                result = tempSession.query(Product).filter_by(codbarra=codProd).first()
                tempSession.close()
                if (result is not None):
                    self.agregarProductoAVenta(result, precio, False)
                    self.actualizarPantalla()
                else:
                    logging.info("Producto No Encontrado ID = " + codProd)
                    QMessageBox.warning(self,"Venta","Producto No Encontrado")

    def agregarProductoAVenta(self, producto, precio, acumular):
        # Me fijo si ya está agregado en la tabla
        totalItem = 0
        totalDto = 0
        item = self.obtenerItemVenta(producto.id, None)
        if (item is not None and acumular == True):
            item.cantidad = item.cantidad + 1
            totalItem = item.precio_venta
        else:
            self.curpos = self.curpos + 1
            newItem = VentaItem(
                posicion = self.curpos,
                sell_id = self.venta.id,
                product_id = producto.id,
                precio_venta = precio if (precio is not None) else (producto.precio_venta),
                cantidad = 1,
                descuento = 0
            )
            totalItem = newItem.precio_venta
            # newItem.product = producto
            self.venta.items.append(newItem)
            # self.session.commit()
        self.setTotalBultos(self.totalBultos + 1)
        self.setTotalVenta(self.venta.total_venta + Decimal("%0.2f" % (totalItem,)), self.venta.total_dto + Decimal("%0.2f" % (totalDto,)))
        self.actualizarPantalla()

    def obtenerItemVenta(self, prod_id, precio_vta):
        if (precio_vta is not None):
            result = self.venta.items.filter(VentaItem.product_id==prod_id, VentaItem.precio_venta==precio_vta).first()
        else:
            result = self.venta.items.filter(VentaItem.product_id==prod_id).first()
        return result

    def imprimirTicket(self):
        if self.model is not None:
            self.pb_ticket.setDisabled(True)
            result,msg,rta = FBWrapper.imprimirTicket(self.venta)
            if (result):
                self.finalizarVenta(True)
            else:
                QMessageBox.critical(self,"Imprimir Ticket",msg)
                self.pb_ticket.setDisabled(False)

    def anularVenta(self):
        if self.model is not None:
            self.session.rollback()
            self.session.close()
            self.nuevaVenta()

    def finalizarVenta(self, status):
        if self.model is not None:
            self.venta.estado = (1 if (status == True) else 0)
            self.session.commit()
            self.session.close()
            self.nuevaVenta()

    def refreshTable(self, data):
        self.model = AlchemicalTableModel(
            self.session, #FIXME pass in sqlalchemy session object
            None,
            data, # sql alchemy mapped object,
            None, # orderby
            [
              ('product_id', VentaItem.product_id, 'product_id', {'editable': False}),
              ('Nombre', VentaItem.product, 'product.nombre', {'editable': False}),
              ('Precio', VentaItem.precio_venta, 'precio_venta', {'editable': False}),
              ('Cantidad', VentaItem.cantidad, 'cantidad', {'editable': False}),
            ])
        self.tb_venta.setModel(self.model.refresh())
        self.tb_venta.setColumnHidden(0, True);
