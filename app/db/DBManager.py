# This Python file uses the following encoding: utf-8
import os
import csv
import pandas as pd
import logging
from sqlite3 import OperationalError
from PyQt5.QtCore import (QObject)
from PyQt5 import QtWidgets
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import asc, desc, func
from db.models.objects import Product
from sqlalchemy.ext.declarative import declarative_base
from db.models.base import Base, engine
from utils import get_project_root

ROOT_PATH = str(get_project_root())

class DBManager(QObject):
    def __init__(self):
        self.engine = engine
        super(QObject, self).__init__()
        # Session = sessionmaker()
        # Session.configure(bind=self.engine)
        # self.session = Session()
        # self.session = self.getNewSession()

    def getNewSession(self):
        Session = sessionmaker()
        Session.configure(bind=self.engine)
        return Session()

    def populate_products(self):
        table_exists = self.engine.dialect.has_table(self.engine, "product")
        if not table_exists:
            print("Tabla products no existe")
            logging.error("Tabla products no existe")
            return None
        session = self.getNewSession()
        product = Product(codbarra="1",nombre="Varios",precio_venta="0",iva="21",enabled=True)
        session.add(product)
        product = Product(codbarra="2",nombre="Carnicería",precio_venta="0",iva="21",enabled=True)
        session.add(product)
        product = Product(codbarra="3",nombre="Fiambre",precio_venta="0",iva="21",enabled=True)
        session.add(product)
        with open(ROOT_PATH + '/db/data/products.csv') as csvDataFile:
            csvReader = csv.reader(csvDataFile)
            for row in csvReader:
                print(row)
                product = (
                    session.query(Product)
                    .filter(Product.codbarra == row[0])
                    .one_or_none()
                )
                if product is None:
                    product = Product(
                        codbarra=row[0],
                        nombre=row[1],
                        precio_venta=row[2],
                        iva=row[3],
                        enabled=True
                    )
                    session.add(product)
            session.commit()
            session.close()

    def __exit__(self):
        # self.session.close()
        pass

    def create_database(self):
        logging.info("starting creating database")
        print("starting creating database")
        # get the author/book/publisher data into a dictionary structure
        Base.metadata.create_all(self.engine)
        logging.info("finished creating database")
        print("finished creating database")

    def build_products(self):
        logging.info("starting populate products")
        print("starting populate products")
        # get the author/book/publisher data into a dictionary structure
        self.populate_products()
        logging.info("finished populate products")
        print("finished populate products")
