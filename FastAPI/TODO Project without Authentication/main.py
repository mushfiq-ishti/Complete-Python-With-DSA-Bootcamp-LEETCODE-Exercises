#here the actual table will be created and the API will be defined
from fastapi import FastAPI, Depends, HTTPException, Path
from database import engine, Base, SessionLocal
import models
from models import Todos
from typing import Annotated
from sqlalchemy.orm import Session 
from pydantic import BaseModel, Field

app = FastAPI() #creating an instance of the FastAPI class
models.Base.metadata.create_all(bind=engine) #creating the tables in the database using the models defined in models.py

#creating DB dependency
def get_db():
    db = SessionLocal() #creating a new session for the database. Will be used everytime we want to interact with the database in the API endpoints
    try:
        yield db #yielding the database session to be used in the API endpoints
    finally:
        db.close() #closing the database session after use



db_dependency = Annotated[SessionLocal, Depends(get_db)] #creating a type annotation for the database dependency to be used in the API endpoints.  The database session is passed as a parameter using the get_db dependency.

class TodoRequest(BaseModel): #creating a Pydantic model for the request body of the API endpoints. This will be used to validate the data sent in the request body and to create a new todo in the database.
    title: str= Field (min_length=3) #id will be auto added by the database, so we don't need to include it in the request body
    description: str= Field (min_length=3, max_length=100) #description will be a string with a minimum length of 3 and a maximum length of 100
    priority: int= Field (ge=0, le=6)
    completed: bool

@app.get('/') #creating a GET endpoint at the root of the API
def read_all(db: db_dependency): #creating a function to read all the todos from the database.
    #dependedncy injection is done to do something before we execute our program, in this case we are creating LocalSession using get_db function and passing it to the read_all function as a parameter, so that we can use the database session to interact with the database in the read_all function
    todos = db.query(Todos).all() #querying the database to get all the todos
    return todos #returning the list of todos as a response to the API call

@app.get('/todo/{todo_id}')
def read_todo(db: db_dependency, todo_id: int=Path(gt=0)):
    todo = db.query(Todos).filter(Todos.id == todo_id).first() #querying the database to get a specific todo by its id
    if todo is not None:
        return todo #returning the todo as a response to the API call
    else:
        #return {"error": "Todo not found"} #returning an error message if the todo is not found
        raise HTTPException(status_code=404, detail="Todo not found") #raising an HTTP exception with a 404 status code and a detail message if the todo is not found

@app.post('/todo') #creating a POST endpoint at the root of the API
def create_todo(db: db_dependency, todo_request: TodoRequest): #creating a function to create a new todo in the database. The request body will be validated using the TodoRequest Pydantic model.
    todo_model=Todos(**todo_request.dict()) #creating a new instance of the Todos model using the data from the request body. The ** operator is used to unpack the dictionary returned by the dict() method of the Pydantic model and pass it as keyword arguments to the Todos model.
    db.add(todo_model) #adding the new todo to the database session
    db.commit() #committing the changes to the database

@app.put('/todo/{todo_id}') #creating a PUT endpoint to update a specific todo by its id
def update_todo(db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)): #creating a function to update a specific todo in the database. The request body will be validated using the TodoRequest Pydantic model.
    todo = db.query(Todos).filter(Todos.id == todo_id).first() #querying the database to get a specific todo by its id
    if todo is not None:
        todo.title = todo_request.title #updating the title of the todo with the new value from the request body
        todo.description = todo_request.description #updating the description of the todo with the new value from the request body
        todo.priority = todo_request.priority #updating the priority of the todo with the new value from the request body
        db.add(todo) #adding the updated todo to the database session
        todo.completed = todo_request.completed #updating the completed status of the todo with the new value from the request body
        db.commit() #committing the changes to the database
        return {"message": "Todo updated successfully"} #returning a success message as a response to the API call
    else:
        raise HTTPException(status_code=404, detail="Todo not found") #raising an HTTP exception with a 404 status code and a detail message if the todo is not found
    
@app.delete('/todo/{todo_id}') #creating a DELETE endpoint to delete a specific todo by its id
def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)): #creating a function to delete a specific todo from the database by its id
    todo = db.query(Todos).filter(Todos.id == todo_id).first() #querying the database to get a specific todo by its id
    if todo is not None:
        db.delete(todo) #deleting the todo from the database session
        db.commit() #committing the changes to the database
        return {"message": "Todo deleted successfully"} #returning a success message as a response to the API call
    else:
        raise HTTPException(status_code=404, detail="Todo not found") #raising an HTTP exception with a 404 status code and a detail message if the todo is not found