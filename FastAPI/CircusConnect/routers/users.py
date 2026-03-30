from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import func
from database import engine, Base, SessionLocal

from models import Likes, Posts, Users
from typing import Annotated
from sqlalchemy.orm import Session 
from pydantic import BaseModel, Field
from .auth import get_current_user
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import UploadFile, File
import uuid

router = APIRouter(
    prefix="/user", 
    tags=["user"]
) 

def get_db():
    db = SessionLocal() 
    try:
        yield db 
    finally:
        db.close()
class PostRequest(BaseModel):
    title: str= Field (min_length=3) 
    description: str= Field (min_length=3, max_length=100) 

db_dependency = Annotated[Session, Depends(get_db)] 
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 

class UserVerification(BaseModel):
    password: str
    new_password: str=Field(min_length=6)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    role: str
    class Config:
        from_attributes = True

@router.get('/', response_model=UserResponse)
def get_user_info(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return db.query(Users).filter(Users.id == user.get('id')).first()

@router.get('/posts')
def read_all_posts_by_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    posts = (
        db.query(Posts, func.count(Likes.id).label("likes"))\
        .outerjoin(Likes, Posts.id == Likes.post_id)\
        .filter(Posts.owner_id == user.get('id'))\
        .group_by(Posts.id)\
        .all()
    )
    return [
        {
            "id": post.id,
            "title": post.title,
            "description": post.description,
            "owner_id": post.owner_id,
            "image_url": post.image_url, 
            "likes": likes,
            "comments": [
                {
                    "id": comment.id,
                    "content": comment.content,
                    "username": comment.owner.username 
                }
                for comment in post.comments 
            ]
        } 
        for post, likes in posts
    ]


    
@router.post('/post')
def create_new_post(user: user_dependency, db: db_dependency, post_request: PostRequest): 
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized") 
    
    post_model=Posts(**post_request.dict(), owner_id=user.get('id')) 
    db.add(post_model) 
    db.commit() 
    return {"message": "Posted successfully!"}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 Megabytes in bytes
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/jpg"]
@router.post('/post/{post_id}/image')
async def upload_image_for_post(user: user_dependency, db: db_dependency, post_id: int = Path(gt=0), file: UploadFile = File(...)):
    
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.owner_id != user.get('id'):
        raise HTTPException(status_code=403, detail="You can only add images to your own posts")

    if file.content_type not in ALLOWED_TYPES: #VALIDATION: Check File Type
        raise HTTPException(status_code=400, detail="Post not found")
        
    file_content = await file.read() #VALIDATION: Check File Size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400,detail="File size cannot exceed 5MB!")

    file_extension = file.filename.split(".")[-1] #Saving the physical file to hard drive
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"static/images/{unique_filename}"

    with open(file_path, "wb") as buffer: #we writing those exact bytes to the disk
        buffer.write(file_content)

    post.image_url = f"/static/images/{unique_filename}" #Saving the text URL to your database
    db.commit()
    return {"message": "Image uploaded successfully!", "image_url": post.image_url}

@router.put('/password')
def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized") 
    user_model = db.query(Users).filter(Users.id == user.get('id')).first() 
    if bcrypt_context.verify(user_verification.password, user_model.hashed_password): 
        user_model.hashed_password = bcrypt_context.hash(user_verification.new_password) 
        db.add(user_model) 
        db.commit() 
        return {"message": "Password updated successfully"} 
    else:
        raise HTTPException(status_code=400, detail="Incorrect password") 
    
@router.delete('/post/{post_id}') 
def delete_post(user: user_dependency, db: db_dependency, post_id: int = Path(gt=0)): 
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized") 
    post = db.query(Posts).filter(Posts.id == post_id).filter(Posts.owner_id == user.get('id')).first() 
    if post is not None:
        db.delete(post) 
        db.commit() 
        return {"message": "Post deleted successfully"} 
    else:
        raise HTTPException(status_code=404, detail="Post not found")

@router.put('/post/{post_id}') 
def edit_post(user:user_dependency,db: db_dependency, post_request: PostRequest, post_id: int = Path(gt=0)): 
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized") 
    post = db.query(Posts).filter(Posts.id == post_id).filter(Posts.owner_id == user.get('id')).first() 
    if post is not None:
        post.title = post_request.title 
        post.description = post_request.description 
        db.add(post) 
        db.commit() 
        return {"message": "Post updated successfully"} 
    else:
        raise HTTPException(status_code=404, detail="Post not found")  