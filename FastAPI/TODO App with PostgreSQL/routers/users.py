from fastapi import APIRouter, Depends, HTTPException, Path
from database import engine, Base, SessionLocal

from models import Todos, Users
from typing import Annotated
from sqlalchemy.orm import Session 
from pydantic import BaseModel, Field
from .auth import get_current_user
from jose import jwt, JWTError
from passlib.context import CryptContext


router = APIRouter(
    prefix="/user", #prefix for all the endpoints in this router, this will be added to the path of all the endpoints in this router, for example if we have an endpoint with path /register in this router, then the actual path of that endpoint will be /auth/register
    tags=["user"]
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
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #creating an instance of the CryptContext class to hash the password

class UserVerification(BaseModel):
    password: str
    new_password: str=Field(min_length=6)

@router.get('/')
def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized") #raising an HTTP exception with a 401 status code and a detail message if the user is not authenticated
    return db.query(Users).filter(Users.id == user.get('id')).first() #querying the database to get a specific user by its id and returning it as a response to the API call

@router.put('/password')
def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized") #raising an HTTP exception with a 401 status code and a detail message if the user is not authenticated
    user_model = db.query(Users).filter(Users.id == user.get('id')).first() #querying the database to get a specific user by its id
    if bcrypt_context.verify(user_verification.password, user_model.hashed_password): #verifying the password using the bcrypt algorithm and the hashed password stored in the database
        user_model.hashed_password = bcrypt_context.hash(user_verification.new_password) #hashing the new password using the bcrypt algorithm and updating the hashed password in the database
        db.add(user_model) #adding the updated user model to the database session
        db.commit() #committing the changes to the database
        return {"message": "Password updated successfully"} #returning a success message as a response to the API call
    else:
        raise HTTPException(status_code=400, detail="Incorrect password") #raising an HTTP exception with a 400 status code and a detail message if the current password is incorrect