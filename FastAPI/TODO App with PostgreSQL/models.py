#what kind of databse tables are we going to have in our database, what are the columns and their data types wil be defined here

from database import Base
from sqlalchemy import Column, Integer, String, Boolean,ForeignKey

class Users(Base):
    __tablename__ = 'users' #name of the table in the database

    id = Column(Integer, primary_key=True, index=True) #id column which is an integer and is the primary key
    email = Column(String, unique=True, index=True) #email column which is a string and is unique and indexed for faster search
    username = Column(String, unique=True, index=True) #username column which is a string and is unique and indexed for faster search
    first_name = Column(String) #first name column which is a string
    last_name = Column(String) #last name column which is a string
    hashed_password = Column(String) #password column which is a string
    is_active = Column(Boolean, default=True) #is active column which is a boolean and has a default value of true
    role = Column(String) #role column which is a string and has a default value of user

class Todos(Base):
    __tablename__ = 'todos' #name of the table in the database

    id = Column(Integer, primary_key=True, index=True) #id column which is an integer and is the primary key
    title = Column(String, index=True) #title column which is a string and is indexed for faster search
    description = Column(String, index=True) #description column which is a string and is indexed for faster search
    priority = Column(Integer, index=True) #priority column which is an integer and is indexed for faster search
    completed = Column(Boolean, default=False) #completed column which is a boolean and has a default value of false
    owner_id = Column(Integer, ForeignKey("users.id")) #owner id column which is an integer and is a foreign key to the users table, this will be used to link the todos to the users who created them
    