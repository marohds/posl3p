from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils import get_project_root


ROOT_PATH = str(get_project_root())

###############################################################################################
# Initialize the database connection and prepare the session                                  #
# create_engine creates the engine that interacts with database                               #
# Class will be used for tables, declarative_base is used to associate which                  #
# class (table) is which in the database.                                                     #
# Session is used to perform CRUD to the database.                                            #
# See tutorial from https://leportella.com/english/2019/01/10/sqlalchemy-basics-tutorial.html #
###############################################################################################
Base = declarative_base()
engine = create_engine('sqlite:///' + ROOT_PATH + '/db/objects2.db', echo=True)
Session = sessionmaker(bind=engine)
