#here the actual table will be created and the API will be defined
from fastapi import FastAPI
from database import engine
import models
from routers import auth, todos,admin,users

app = FastAPI() #creating an instance of the FastAPI class
models.Base.metadata.create_all(bind=engine) #creating the tables in the database using the models defined in models.py

app.include_router(auth.router) #including the router for the authentication endpoints in the FastAPI app
app.include_router(todos.router) #including the router for the todos endpoints in the FastAPI app
app.include_router(admin.router) #including the router for the admin endpoints in the FastAPI app
app.include_router(users.router) #including the router for the user endpoints in the FastAPI app