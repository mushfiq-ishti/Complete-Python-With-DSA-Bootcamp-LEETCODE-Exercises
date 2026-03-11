from fastapi import APIRouter, Depends, HTTPException, Path
from database import engine, Base, SessionLocal

from models import Todos
from typing import Annotated
from sqlalchemy.orm import Session 
from pydantic import BaseModel, Field
from .auth import get_current_user
from jose import jwt, JWTError


router = APIRouter(prefix="/admin", 
    tags=["admin"]
    ) #creating an instance of the FastAPI class


#creating DB dependency
def get_db():
    db = SessionLocal() #creating a new session for the database. Will be used everytime we want to interact with the database in the API endpoints
    try:
        yield db #yielding the database session to be used in the API endpoints
    finally:
        db.close() #closing the database session after use



db_dependency = Annotated[SessionLocal, Depends(get_db)] #creating a type annotation for the database dependency to be used in the API endpoints.  The database session is passed as a parameter using the get_db dependency.
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todos")
def read_all_todos(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized") #raising an HTTP exception with a 401 status code and a detail message if the user is not authenticated
    if user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Forbidden") #raising an HTTP exception with a 403 status code and a detail message if the user is not an admin
    todos = db.query(Todos).all() #querying the database to get all the todos
    return todos #returning the list of todos as a response to the API call 

@router.delete("/todo/{todo_id}")
def delete_todo(user: user_dependency, db: db_dependency, todo_id: int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized") #raising an HTTP exception with a 401 status code and a detail message if the user is not authenticated
    if user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Forbidden") #raising an HTTP exception with a 403 status code and a detail message if the user is not an admin
    todo = db.query(Todos).filter(Todos.id == todo_id).first() #querying the database to get a specific todo by its id
    if todo is not None:
        db.delete(todo) #deleting the todo from the database
        db.commit() #committing the changes to the database
        return {"message": "Todo deleted successfully"} #returning a success message as a response to the API call
    else:
        raise HTTPException(status_code=404, detail="Todo not found") #raising an HTTP exception with a 404 status code and a detail message if the todo is not found