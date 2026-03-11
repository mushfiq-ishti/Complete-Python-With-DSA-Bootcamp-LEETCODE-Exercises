from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:foodbangladesh@localhost/TodoAppDatabase' #creating a location on the fastAPI application to store the database
#todos app db wll have 2 tables. One for user another for todo lis
engine = create_engine(SQLALCHEMY_DATABASE_URL) #creating the database engine which is used to openup connection and close
#allowing only one thread to connect for now

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #session local will become actual database in the future
Base= declarative_base() #object of a database model, which will be used to create tables in the database