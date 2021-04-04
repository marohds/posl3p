# https://gist.github.com/uetoyo/d2ed88b3735b2617fe91
from __future__ import absolute_import, print_function
import functools
from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSignalMapper, QSize, QTextStream, Qt, QAbstractTableModel, QVariant)
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QMdiArea, QMessageBox, QTextEdit, QWidget)
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtSql import QSqlTableModel, QSqlDatabase
from db.DBManager import DBManager
from db.models.objects import Product
from db.models.qvariantalchemy import String, Integer, Boolean, DateTime
from datetime import datetime
from dateutil.parser import parse

from pprint import pprint


def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)

def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))


class AlchemicalTableModel(QAbstractTableModel):
    """
    A Qt Table Model that binds to a SQL Alchemy query
    Example:
    >>> model = AlchemicalTableModel(Session, [('Name', Entity.name)])
    >>> table = QTableView(parent)
    >>> table.setModel(model)
    """

    def __init__(self, session, session_with_query, data, orderby, columns):
        super(AlchemicalTableModel, self).__init__()
        #TODO self.sort_data = [Qt.DescendingOrder,0]
        self.session = session
        self.fields = columns
        self.query = session_with_query
        self.data = data

        self.results = None
        self.count = None
        self.sort = orderby
        self.filter = None

        #self.refresh()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
                return QVariant(self.fields[col][0])
        return QVariant()

#    def sort(self, col, order):
#        """sort table by given column number col"""
#        self.emit(SIGNAL("layoutAboutToBeChanged()"))
#        self.mylist = sorted(self.mylist,
#            key=operator.itemgetter(col))
#        if order == Qt.DescendingOrder:
#            self.mylist.reverse()
#        self.emit(SIGNAL("layoutChanged()"))

    def setFilter(self, filter):
        """Sets or clears the filter, clear the filter by setting to None"""
        self.filter = filter
        self.refresh()

    def refresh(self):
        """Recalculates, self.results and self.count"""

        self.layoutAboutToBeChanged.emit()

        if (self.data is not None):
            self.results = self.data
            self.count = len(self.data)
        else:
            q = self.query
            if self.sort is not None:
                order, col = self.sort
                col = self.fields[col][1]
                if order == Qt.DescendingOrder:
                    col = col.desc()
            else:
                col = None
            if self.filter is not None:
                q = q.filter(self.filter)
            q = q.order_by(col)
            self.results = q.all()
            self.count = q.count()

        self.layoutChanged.emit()
        return self

    def flags(self, index):
        _flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        if self.sort is not None:
                order, col = self.sort

                if self.fields[col][3].get('dnd', False) and index.column() == col:

                        _flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

        if self.fields[index.column()][3].get('editable', False):
                _flags |= Qt.ItemIsEditable

        return _flags

    def supportedDropActions(self):
        return Qt.MoveAction

    def dropMimeData(self, data, action, row, col, parent):
        if action != Qt.MoveAction:
                return

        return False

    def rowCount(self, parent):
        return self.count or 0

    def columnCount(self, parent):
        return len(self.fields)

    def data(self, index, role):
        if not index.isValid():
                return QVariant()

        elif role not in (Qt.DisplayRole, Qt.EditRole):
                return QVariant()

        row = self.results[index.row()]
        name = self.fields[index.column()][2]

        value = rgetattr(row, name)

        if isinstance(value, datetime):
            value = str(value.strftime("%d/%m/%Y %H:%M:%S"))
        else:
            value = str(value)
        return value
        # return str(getattr(row, name))

    def setData(self, index, value, role=None):
        row = self.results[index.row()]
        name = self.fields[index.column()][2]

        try:
                rsetattr(row, name, (value if isinstance(value, str) else value.toString()))
                # setattr(row, name, (value if isinstance(value, str) else value.toString()))
        except Exception as ex:
                QMessageBox.critical(None, 'SQL Error', str(ex))
                return False
        else:
                self.dataChanged.emit(index, index)
                return True

    def sort(self, col, order):
        """Sort table by given column number."""
        self.sort = order, col
        self.refresh()

