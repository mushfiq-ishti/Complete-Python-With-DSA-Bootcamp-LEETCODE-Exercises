#we will use a router to create a separate file for the authentication endpoints, so that we can keep our code organized and modular. We will import this router in the main.py file and include it in the FastAPI app.
# we will have different endpints with different fastapi file on top of our main file
#API router is used to route from main file to auth file

#hasing will be done using passlib and bcrypt 4.0.1s

from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, APIRouter, HTTPException
from pydantic import BaseModel, Field
from models import Users
from passlib.context import CryptContext
from database import engine, Base, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

#app = FastAPI()
router = APIRouter(
    prefix="/auth", #prefix for all the endpoints in this router, this will be added to the path of all the endpoints in this router, for example if we have an endpoint with path /register in this router, then the actual path of that endpoint will be /auth/register
    tags=["auth"] #tags for the endpoints in this router, this will be used to group the endpoints in the documentation, for example all the endpoints in this router will be grouped under the "auth" tag in the documentation
    ) #creating an instance of the APIRouter class to create a router for the authentication endpoints

SECRET_KEY = "your_secret_key" #secret key to encode and decode the JWT tokens, in real application we will use a more secure secret key and store it in an environment variable
ALGORITHM = "HS256" #algorithm to encode and decode the JWT tokens, we will

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #creating an instance of the CryptContext class to hash the password
oauth2_bearer=OAuth2PasswordBearer(tokenUrl="auth/token") #creating an instance of the OAuth2PasswordBearer class to create a dependency for the protected endpoints, this will be used to get the token from the request header and verify it in the protected endpoints

class CreateUserRequest(BaseModel): #creating a Pydantic model for the request body of the user registration endpoint. This will be used to validate the data sent in the request body and to create a new user in the database.
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role:str

class Token(BaseModel): #creating a Pydantic model for the response body of the login endpoint. This will be used to return the JWT token to the user after successful authentication.
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal() #creating a new session for the database. Will be used everytime we want to interact with the database in the API endpoints
    try:
        yield db #yielding the database session to be used in the API endpoints
    finally:
        db.close() #closing the database session after use
db_dependency = Annotated[SessionLocal, Depends(get_db)]

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(Users).filter(Users.username == username).first() #querying the database to get a specific user by its username
    if user is not None:
        if bcrypt_context.verify(password, user.hashed_password): #verifying the password using the bcrypt algorithm and the hashed password stored in the database
            return user #returning the user object if the authentication is successful
        return False #returning false if the password is incorrect
    return False #returning false if the authentication is unsuccessful


# @router.get('/auth/')
# def get_user():
#     return {"message": "This is the authentication endpoint"}

def create_access_token(username:str, user_id:int,role:str, expires_delta:timedelta):
    encode={'sub':username,'id':user_id,'role':role} #creating a dictionary to store the data that we want to include in the JWT token, we will include the username and user id in the token, so that we can use it to verify the token in the protected endpoints
    expires=datetime.utcnow() + expires_delta
    encode.update({"exp":expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload=jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"username": username, "id": user_id, "role": user_role}
    except JWTError: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@router.post('/',status_code=status.HTTP_201_CREATED) #creating a POST endpoint for user registration at the /auth/register path
def create_user(db:db_dependency,create_user_request: CreateUserRequest): #creating a function to create a new user in the database. The request body will be validated using the CreateUserRequest Pydantic model.
    #create_user_model=Users(**create_user_request.dict()) #will give error as we are not passing the hashed password to the Users model, we need to hash the password before creating the user in the database
    create_user_model=Users( 
    email=create_user_request.email,
    username=create_user_request.username,
    first_name=create_user_request.first_name,
    last_name=create_user_request.last_name,
    role=create_user_request.role,
    hashed_password=bcrypt_context.hash(create_user_request.password), #hashing the password using the bcrypt algorithm and passing it to the Users model
    is_active=True
    )
    db.add(create_user_model) #returning the created user as a response to the API call, in real application we will not return the user object as it contains the hashed password, we will return a success message instead
    db.commit() #committing the changes to the database

#token is returned to user with all login information
#multipart will be used to create different endpoints for different types of users, for example we can have a separate endpoint for admin users and another endpoint for regular users, this will help us to implement role based access control in our application
#use pip install multipart
#pip install "python-jose[cryptography]" to create and verify JWT tokens, we will use JWT tokens for authentication in our application, we will create a token when the user logs in and return it as a response to the API call, and we will verify the token in the protected endpoints to allow access only to authenticated users.
@router.post('/token',response_model=Token) #creating a POST endpoint for user login at the /auth/token path, this endpoint will return a JWT token to the user after successful authentication
def login_for_acess_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user=authenticate_user(db, form_data.username, form_data.password) #authenticating the user using the authenticate_user function
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password") #raising an HTTP exception with a 401 status code and a detail message if the authentication is unsuccessful
    token=create_access_token(user.username, user.id, user.role, expires_delta=timedelta(minutes=20)) #creating a JWT token for the authenticated user with an expiration time of 30 minutes
    #return token #returning a token as a response to the API call, in real application we will return a JWT token instead of the username, but for simplicity we are returning the username as the token in this example
    return {'access_token': token, 'token_type': 'bearer'} #returning the JWT token and the token type as a response to the API call