#what kind of databse tables are we going to have in our database, what are the columns and their data types wil be defined here

from database import Base
from sqlalchemy import Column, Integer, String, Boolean

class Todos(Base):
    __tablename__ = 'todos' #name of the table in the database

    id = Column(Integer, primary_key=True, index=True) #id column which is an integer and is the primary key
    title = Column(String, index=True) #title column which is a string and is indexed for faster search
    description = Column(String, index=True) #description column which is a string and is indexed for faster search
    priority = Column(Integer, index=True) #priority column which is an integer and is indexed for faster search
    completed = Column(Boolean, default=False) #completed column which is a boolean and has a default value of false

    