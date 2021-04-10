import datetime as dt
import pytz
import logging
from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSignalMapper, QSize, QTextStream, Qt, pyqtSlot, QModelIndex)
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QMdiArea, QMessageBox, QTextEdit, QWidget, QTableView)
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import QFont
from db.DBManager import DBManager
from db.models.objects import Venta, Cierre
from db.models.alchemicaltablemodel import AlchemicalTableModel
from views.product.edit import ProductoEditView
from sqlalchemy import desc, func
from ws.fbwrapper import FBWrapper
# from sqlalchemy_paginator import Paginator
from pprint import pprint
from utils import get_project_root


ROOT_PATH = str(get_project_root())

class CierreIndexView(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(QWidget, self).__init__()
        self.ui = uic.loadUi(ROOT_PATH + "/layouts/cierre/index.ui", self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.model = None
        self.isUntitled = True
        self.connectEvents()
        self.dbm = DBManager()
        self.dt_desde.setDate(dt.date.today())
        self.dt_hasta.setDate(dt.date.today())
        fnt = QFont("Arial", 18)
        self.tv_ventas.setFont(fnt)
        self.cargarCierres()

    def cargarCierres(self):
        f_desde = dt.datetime(self.dt_desde.date().year(), self.dt_desde.date().month(), self.dt_desde.date().day(),0,0,0)
        f_hasta = dt.datetime(self.dt_hasta.date().year(), self.dt_hasta.date().month(), self.dt_hasta.date().day(),23,59,59)
        timezone = pytz.timezone("America/Argentina/Buenos_Aires")
        f_desde = timezone.localize(f_desde).astimezone(pytz.utc)
        f_hasta = timezone.localize(f_hasta).astimezone(pytz.utc)
        if (f_desde <= f_hasta):
            tempSession = self.dbm.getNewSession()
            cierreQuery = tempSession.query(func.sum(Venta.total_venta).label("total_venta"), func.sum(Venta.total_dto).label("total_dto"), Cierre.id, Cierre.created_at).join(Venta).group_by(Cierre.id)
            tempQuery = cierreQuery.filter(Cierre.created_at >= f_desde).filter(Cierre.created_at <= f_hasta)
            self.refreshTable(tempQuery, tempSession)
            tempSession.close()

    def __del__(self):
        pass

    def cierreZ(self):
        self.pb_cierrez.setDisabled(True)
        result, msg, rta = FBWrapper.cierreZ()
        if (result):
            print(msg)
            QMessageBox.information(self, "Cierre Z", "Se envió a imprimir el Cierre Z<br />Verifique la impresora.<br />" + msg)
        else:
            print(msg)
            QMessageBox.critical(self, "Cierre Z", msg)
        self.pb_cierrez.setDisabled(False)

    def connectEvents(self):
        self.pb_buscar.clicked.connect(self.cargarCierres)
        self.pb_cierrez.clicked.connect(self.cierreZ)

    def refreshTable(self, query, session):
        self.model = AlchemicalTableModel(
            session,  # FIXME pass in sqlalchemy session object
            query,  # sql alchemy mapped object
            None,  # data
            [Qt.DescendingOrder, 0],  # orderby
            [
              ('N°', Cierre.id, 'id', {'editable': False}),
              ('Fecha de Cierre', Cierre.created_at, 'created_at', {'editable': False}),
              ('Importe Total', Venta.total_venta, 'total_venta', {'editable': False}),
              ('Descuento', Venta.total_dto, 'total_dto', {'editable': False}),
            ])
        self.tv_ventas.setModel(self.model.refresh())
        header = self.tv_ventas.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setStyleSheet("QHeaderView { font-size: 18pt; font-weight: bold }")
