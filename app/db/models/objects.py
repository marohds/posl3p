from db.models.base import Base
from db.models.sqlitedecimal import SqliteDecimal
from sqlalchemy import Column, ForeignKey, Table, UniqueConstraint, sql
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from db.models.qvariantalchemy import String, Integer, Boolean, DateTime, Enum
from datetime import datetime

#####################################################################################
# If __tablename__ is not declared the class name will be the assumed table name.   #
# This declares the structure of the tables, AsaObjects is the class to create      #
# the structure of the table where it has id as primary key, obj_name, host_address #
# and description as columns.                                                       #
#####################################################################################

class Cierre(Base):
    __tablename__ = 'cierre'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=sql.func.now())
    ventas = relationship("Venta", lazy='dynamic')

class VentaItem(Base):
    __tablename__ = 'sell_item'
    posicion = Column(Integer, primary_key=True)
    sell_id = Column(Integer, ForeignKey('sell.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), primary_key=True)
    precio_venta = Column(SqliteDecimal(2))
    descuento = Column(SqliteDecimal(2))
    cantidad = Column(Integer)
    product = relationship("Product", lazy='joined')

class Venta(Base):
    __tablename__ = 'sell'
    id = Column(Integer, primary_key=True)
    estado = Column(Integer)
    total_venta = Column(SqliteDecimal(2))
    total_dto = Column(SqliteDecimal(2))
    created_at = Column(DateTime(timezone=True), server_default=sql.func.now())
    cierre_id = Column(Integer, ForeignKey('cierre.id'), nullable=True)
    items = relationship("VentaItem", lazy='dynamic', cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True)
    codbarra = Column(String)
    nombre = Column(String, nullable=False)
    precio_venta = Column(SqliteDecimal(2), nullable=False)
    iva = Column(SqliteDecimal(2), nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
