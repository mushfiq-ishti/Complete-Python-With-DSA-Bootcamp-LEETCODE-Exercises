from fastapi import APIRouter, Depends, HTTPException, Path
from database import engine, Base, SessionLocal

from models import Likes, Posts, Users, Comments
from typing import Annotated
from sqlalchemy.orm import Session 
from pydantic import BaseModel, Field
from .auth import get_current_user
from jose import jwt, JWTError


router = APIRouter(prefix="/admin", 
    tags=["admin"]
    ) 

def get_db():
    db = SessionLocal() 
    try:
        yield db 
    finally:
        db.close() 

db_dependency = Annotated[Session, Depends(get_db)] 
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/users")
def read_all_users(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized") 
    if user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Forbidden") 
    users = db.query(Users).all()
    return users 

@router.delete('/likes/{post_id}')
def delete_likes_from_post(user: user_dependency, db: db_dependency, post_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized") 
    if user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Forbidden") 
    db.query(Likes).filter(Likes.post_id == post_id).delete()
    db.commit()
    return {"message": "deleted all likes from the post"}

@router.delete("/post/{post_id}")
def delete_post(user: user_dependency, db: db_dependency, post_id: int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized") 
    if user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Forbidden") 
    post = db.query(Posts).filter(Posts.id == post_id).first() 
    if post is not None:
        db.query(Comments).filter(Comments.post_id == post_id).delete() # Delete all comments on this post
        db.query(Likes).filter(Likes.post_id == post_id).delete() #Delete all likes on this post
        db.delete(post) #Finally, delete the post itself
        db.commit() 
        return {"message": "Post, comments, and likes deleted successfully"} 
    else:
        raise HTTPException(status_code=404, detail="Post not found") 
    
# @router.delete("/user/{user_id}")
# def delete_user(user: user_dependency, db: db_dependency, user_id: int=Path(gt=0)):
#     if user is None:
#         raise HTTPException(status_code=401, detail="Unauthorized") 
#     if user.get('role') != 'admin':
#         raise HTTPException(status_code=403, detail="Forbidden") 
#     user_model = db.query(Users).filter(Users.id == user_id).first() 
#     if user_model is not None:
#         db.delete(user_model) 
#         db.commit() 
#         return {"message": "User deleted successfully"} 
#     else:
#         raise HTTPException(status_code=404, detail="User not found") 

@router.delete("/user/{user_id}")
def delete_user(user: user_dependency, db: db_dependency, user_id: int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized") 
    if user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Forbidden") 
    user_model = db.query(Users).filter(Users.id == user_id).first() 
    if user_model is not None:
        db.query(Comments).filter(Comments.owner_id == user_id).delete()  # Delete every comment and like this user made on OTHER people's posts
        db.query(Likes).filter(Likes.owner_id == user_id).delete()
        user_posts = db.query(Posts).filter(Posts.owner_id == user_id).all() #Find all posts created by this user
        
        for post in user_posts:   #Loop through their posts and delete all associated comments/likes
            db.query(Comments).filter(Comments.post_id == post.id).delete()
            db.query(Likes).filter(Likes.post_id == post.id).delete()
            db.delete(post) # Delete the post itself
            
        db.delete(user_model) #Finally, delete the user
        db.commit() 
        
        return {"message": "User and all associated data deleted successfully"} 
    else:
        raise HTTPException(status_code=404, detail="User not found")