from sqlalchemy.types import TypeDecorator
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Numeric, Boolean
from sqlalchemy import Integer, Text, Column
from decimal import Decimal


class SqliteDecimal(TypeDecorator):
    # This TypeDecorator use Sqlalchemy Integer as impl. It converts Decimals
    # from Python to Integers which is later stored in Sqlite database.
    impl = Integer

    def __init__(self, scale):
        # It takes a 'scale' parameter, which specifies the number of digits
        # to the right of the decimal point of the number in the column.
        TypeDecorator.__init__(self)
        self.scale = scale
        self.multiplier_int = 10 ** self.scale

    def process_bind_param(self, value, dialect):
        # e.g. value = Column(SqliteDecimal(2)) means a value such as
        # Decimal('12.34') will be converted to 1234 in Sqlite
        if value is not None:
            # value = int(Decimal(value) * self.multiplier_int)
            value = int(float(value) * self.multiplier_int)
        return value

    def process_result_value(self, value, dialect):
        # e.g. Integer 1234 in Sqlite will be converted to Decimal('12.34'),
        # when query takes place.
        if value is not None:
            # value = Decimal(value) / self.multiplier_int
            value = Decimal("%0.2f" % (value,)) / self.multiplier_int
        return value
