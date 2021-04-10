import datetime as dt
import pytz
import logging
from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSignalMapper, QSize, QTextStream, Qt, pyqtSlot, QModelIndex)
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QMdiArea, QMessageBox, QTextEdit, QWidget, QTableView)
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import QFont
from db.DBManager import DBManager
from db.models.objects import Venta, VentaItem
from db.models.alchemicaltablemodel import AlchemicalTableModel
from views.product.edit import ProductoEditView
from sqlalchemy import desc, func
from ws.fbwrapper import FBWrapper
from pprint import pprint
from utils import get_project_root


ROOT_PATH = str(get_project_root())

class VentaIndexView(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(QWidget, self).__init__()
        self.ui = uic.loadUi(ROOT_PATH + "/layouts/venta/index.ui", self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.model = None
        self.isUntitled = True
        self.connectEvents()
        self.dbm = DBManager()
        self.dt_desde.setDate(dt.date.today())
        self.dt_hasta.setDate(dt.date.today())
        self.selectedVenta = None
        fnt = QFont("Arial", 18)
        self.tv_detail.setFont(fnt)
        self.tv_ventas.setFont(fnt)
        self.cargarVentas()

    def cargarVentas(self):
        f_desde = dt.datetime(self.dt_desde.date().year(), self.dt_desde.date().month(), self.dt_desde.date().day(),0,0,0)
        f_hasta = dt.datetime(self.dt_hasta.date().year(), self.dt_hasta.date().month(), self.dt_hasta.date().day(),23,59,59)
        timezone = pytz.timezone("America/Argentina/Buenos_Aires")
        f_desde = timezone.localize(f_desde).astimezone(pytz.utc)
        f_hasta = timezone.localize(f_hasta).astimezone(pytz.utc)
        if (f_desde <= f_hasta):
            session = self.dbm.getNewSession()
            ventasQuery = session.query(Venta)
            totalesQuery = session.query(
                                    func.count(Venta.id).label('ventas'),
                                    func.sum(Venta.total_venta).label('total'),
                                )
            tempQuery = ventasQuery.filter(Venta.created_at >= f_desde).filter(Venta.created_at <= f_hasta)
            countQuery = totalesQuery.filter(Venta.created_at >= f_desde).filter(Venta.created_at <= f_hasta).one()
            self.lblCount.setText('<html><head/><body><p><span style="font-size:24pt;">' + str(countQuery[0] or 0) + '</span></p></body></html>')
            self.lblTotal.setText('<html><head/><body><p><span style="font-size:24pt;">$ ' + str(countQuery[1] or 0) + '</span></p></body></html>')
            self.refreshTable(tempQuery, session)
            session.close()
        else:
            QMessageBox.warning(self, "Consulta de Ventas", "La fecha <Desde> debe ser menor o igual que <Hasta>")

    def __del__(self):
        pass

    def connectEvents(self):
        self.pb_buscar.clicked.connect(self.cargarVentas)
        self.tv_ventas.clicked.connect(self.tableVentasClicked)
        self.pb_ticket.clicked.connect(self.imprimirTicket)

    def imprimirTicket(self):
        if (self.selectedVenta.estado != 0):
            ret = QMessageBox.question(self,'', "Ya se realizó una impresión de este ticket. ¿Volver a imprimir?", QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.No:
                return
        result,msg,rta = FBWrapper.imprimirTicket(self.selectedVenta)
        if (result):
            QMessageBox.information(self,'Imprimir Ticket','Se ha enviado a imprimir correctamente.')
        else:
            QMessageBox.critical(self,"Imprimir Ticket",msg)
            self.pb_ticket.setDisabled(False)



    @pyqtSlot(QModelIndex)
    def tableVentasClicked(self, index):
        venta_id = int(index.model().index(index.row(), 0).data())
        session = self.dbm.getNewSession()
        self.selectedVenta = session.query(Venta).filter(Venta.id == venta_id).one()
        model = AlchemicalTableModel(
            session, #FIXME pass in sqlalchemy session object
            self.selectedVenta.items, #sql alchemy mapped object
            None, # Data
            None, # Orderby
            [
              ('N°', VentaItem.posicion, 'posicion', {'editable': False}),
              ('Cod', VentaItem.product, 'product.codbarra', {'editable': False}),
              ('Nombre', VentaItem.product, 'product.nombre', {'editable': False}),
              ('Precio', VentaItem.precio_venta, 'precio_venta', {'editable': False}),
              ('Cantidad', VentaItem.cantidad, 'cantidad', {'editable': False}),
              # ('Descuento', VentaItem.descuento, 'descuento', {'editable': False}),
            ])
        self.tv_detail.setModel(model.refresh())
        header = self.tv_detail.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setStyleSheet("QHeaderView { font-size: 18pt; font-weight: bold }")



        self.pb_ticket.setVisible(True)
        session.close()

    def refreshTable(self, query, session):
        self.model = AlchemicalTableModel(
            session, #FIXME pass in sqlalchemy session object
            query, #sql alchemy mapped object
            None,
            [Qt.DescendingOrder,0], # orderby
            [
              ('id', Venta.id, 'id', {'editable': False}),
              ('Fecha', Venta.created_at, 'created_at', {'editable': False}),
              ('Total', Venta.total_venta, 'total_venta', {'editable': False}),
              ('Descuento', Venta.total_dto, 'total_dto', {'editable': False}),
              ('Estado', Venta.estado, 'estado', {'editable': False}),
            ])
        self.tv_ventas.setModel(self.model.refresh())
        header = self.tv_ventas.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setStyleSheet("QHeaderView { font-size: 18pt; font-weight: bold }")
