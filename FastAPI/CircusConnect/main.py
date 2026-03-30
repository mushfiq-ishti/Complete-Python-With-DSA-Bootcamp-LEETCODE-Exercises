from fastapi import FastAPI
from routers import posts
from database import engine
import models
from routers import auth, admin,users
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI() 
os.makedirs("static/images", exist_ok=True) #bydefault fastapi won't let us see local static files 
app.mount("/static", StaticFiles(directory="static"), name="static") #to serve this folder to the internet

models.Base.metadata.create_all(bind=engine) 

app.include_router(auth.router) 
app.include_router(posts.router) 
app.include_router(admin.router) 
app.include_router(users.router) 