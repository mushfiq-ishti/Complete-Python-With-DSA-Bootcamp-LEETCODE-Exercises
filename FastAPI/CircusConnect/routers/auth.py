from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, APIRouter, HTTPException, Response, Cookie
from pydantic import BaseModel, Field
from models import Users
from passlib.context import CryptContext
from database import engine, Base, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
    prefix="/auth", 
    tags=["auth"] 
    ) 

SECRET_KEY = "your_secret_key" 
ALGORITHM = "HS256" 

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 
oauth2_bearer=OAuth2PasswordBearer(tokenUrl="auth/token") 

class CreateUserRequest(BaseModel): 
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role:str

class Token(BaseModel): 
    access_token: str
    token_type: str
    refresh_token: str 

# class RefreshTokenRequest(BaseModel): #wont be needed if we fetch this by http only cookie
#     refresh_token: str

def get_db():
    db = SessionLocal() 
    try:
        yield db 
    finally:
        db.close() 
db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(Users).filter(Users.username == username).first() 
    if user is not None:
        if bcrypt_context.verify(password, user.hashed_password): 
            return user 
        return False 
    return False 


def create_access_token(username:str, user_id:int,role:str, expires_delta:timedelta):
    encode={'sub':username,'id':user_id,'role':role} 
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

@router.post('/CreateUser',status_code=status.HTTP_201_CREATED) 
def create_new_user(db:db_dependency,create_user_request: CreateUserRequest): 
    create_user_model=Users( 
    email=create_user_request.email,
    username=create_user_request.username,
    first_name=create_user_request.first_name,
    last_name=create_user_request.last_name,
    role=create_user_request.role,
    hashed_password=bcrypt_context.hash(create_user_request.password), 
    is_active=True
    )
    db.add(create_user_model) 
    db.commit()
    return {"User Created Successfully"} 


# @router.post('/token',response_model=Token) 
# def login_for_acess_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
#     user=authenticate_user(db, form_data.username, form_data.password) 
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password") 
#     token=create_access_token(user.username, user.id, user.role, expires_delta=timedelta(minutes=20)) 
#     refresh=create_access_token(user.username, user.id, user.role, expires_delta=timedelta(days=7))
#     return {'access_token': token, 'token_type': 'bearer', 'refresh_token': refresh}

@router.post('/token') 
def login_for_acess_token(
    response: Response, # accessing to the response object to attach the cookie
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: db_dependency
):
    user = authenticate_user(db, form_data.username, form_data.password) 
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") 
        
    token = create_access_token(user.username, user.id, user.role, expires_delta=timedelta(minutes=20)) 
    refresh = create_access_token(user.username, user.id, user.role, expires_delta=timedelta(days=7)) 
    
    # NEW: Attach the refresh token to an HttpOnly cookie
    response.set_cookie(
        key="refresh_token", 
        value=refresh, 
        httponly=True,  
        max_age=7 * 24 * 60 * 60, 
        samesite="lax", # Protecting against Cross-Site Request Forgery (CSRF)
        secure=False    
    )
    
    return {
        'access_token': token, 
        'token_type': 'bearer'
    }

# @router.post('/refresh', response_model=Token)
# def refresh_access_token(request: RefreshTokenRequest,db: db_dependency):
#     try:
#         payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         user_id: int = payload.get("id")
#         user_role: str = payload.get("role")
#         if username is None or user_id is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
#         new_access_token = create_access_token(username, user_id, user_role, expires_delta=timedelta(minutes=20))
#         new_refresh_token = create_access_token(username, user_id, user_role, expires_delta=timedelta(days=7))
#         return {'access_token': new_access_token, 'token_type': 'bearer', 'refresh_token': new_refresh_token}
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

@router.post('/refresh')
def refresh_access_token(
    response: Response, 
    db: db_dependency, 
    refresh_token: str = Cookie(None) #FastAPI automatically looks for a cookie named 'refresh_token'
):
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        # Decoding the cookie token just like before
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
            
        new_access_token = create_access_token(username, user_id, user_role, expires_delta=timedelta(minutes=20))
        new_refresh_token = create_access_token(username, user_id, user_role, expires_delta=timedelta(days=7))
        
        # Attaching the NEW refresh token to the cookie (overwriting the old one)
        response.set_cookie(
            key="refresh_token", 
            value=new_refresh_token, 
            httponly=True, 
            max_age=7 * 24 * 60 * 60, 
            samesite="lax",
            secure=False 
        )
        # Handing back the new access token
        return {
            'access_token': new_access_token, 
            'token_type': 'bearer'
        }
    except JWTError: 
        raise HTTPException(status_code=401, detail="Refresh token expired. Please log in again.")