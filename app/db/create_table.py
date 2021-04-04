from models.Objects import Product
from models.Base import Base, engine
 
# Create the table ASA_OBJECTS, do not create again if table exists.
if not engine.dialect.has_table(engine, Product.__tablename__):
    Base.metadata.create_all(engine)
