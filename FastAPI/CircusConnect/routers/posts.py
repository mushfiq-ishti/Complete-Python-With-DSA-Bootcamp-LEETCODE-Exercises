from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import func
from database import engine, Base, SessionLocal
from models import Comments, Likes, Posts, CommentsReply
from typing import Annotated
from sqlalchemy.orm import Session 
from pydantic import BaseModel, Field
from .auth import get_current_user
from jose import jwt, JWTError

router = APIRouter() 

def get_db():
    db = SessionLocal() 
    try:
        yield db 
    finally:
        db.close() 

db_dependency = Annotated[Session, Depends(get_db)] 
user_dependency = Annotated[dict, Depends(get_current_user)]     

class CommentRequest(BaseModel):
    content: str = Field(min_length=3, max_length=200)


# @router.get('/') 
# def read_all_posts(user: user_dependency, db: db_dependency):
    
#     if user is None:
#         raise HTTPException(status_code=401, detail="Unauthorized") 

#     posts = db.query(Posts, func.count(Likes.id).label("likes"))\
#         .outerjoin(Likes, Posts.id == Likes.post_id)\
#         .group_by(Posts.id)\
#         .all()
    
#     return [
#         {
#             "id": post.id,
#             "title": post.title,
#             "description": post.description,
#             "owner_id": post.owner_id,
#             "image_url": post.image_url,
#             "likes": likes,
#             "comments": [
#                 {
#                     "id": comment.id,
#                     "content": comment.content,
#                     #"owner_id": comment.owner_id,
#                     "username": comment.owner.username 
#                 }
#                 for comment in post.comments 
#             ]
#         } 
#         for post, likes in posts
#     ]

@router.get('/') 
def read_all_posts(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized") 

    posts = db.query(Posts, func.count(Likes.id).label("likes"))\
        .outerjoin(Likes, Posts.id == Likes.post_id)\
        .group_by(Posts.id)\
        .all()
    
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
                    "username": comment.owner.username,
                    "replies": [
                        {
                            "id": reply.id,               
                            "content": reply.content,     
                            "owner_id": reply.owner_id    
                        }
                        for reply in comment.replies      
                    ]
                }
                for comment in post.comments 
            ]
        } 
        for post, likes in posts
    ]

@router.post('/like/{post_id}')
def like_a_post(user: user_dependency, db: db_dependency, post_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not db.query(Posts).filter(Posts.id == post_id).first():
        raise HTTPException(status_code=404, detail="Post not found")
    if db.query(Likes).filter(Likes.post_id == post_id).filter(Likes.owner_id == user.get('id')).first():
        db.query(Likes).filter(Likes.post_id == post_id).filter(Likes.owner_id == user.get('id')).delete()
        db.commit()
        return {"message": "Unliked successfully!"}
    like_model = Likes(post_id=post_id, owner_id=user.get('id'))
    db.add(like_model)
    db.commit()
    return {"message": "Post liked successfully!"}

@router.post('/comment/{post_id}')
def add_comment(user: user_dependency, db: db_dependency, comment: CommentRequest, post_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    if not db.query(Posts).filter(Posts.id == post_id).first():
        raise HTTPException(status_code=404, detail="Post not found")
    
    comment_model = Comments(content=comment.content, post_id=post_id, owner_id=user.get('id'))
    
    db.add(comment_model)
    db.commit()
    return {"message": "Comment added successfully!"}

@router.post('/commentreply/{comment_id}')
def add_reply_to_comment(user: user_dependency, db: db_dependency, comment: CommentRequest, comment_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    if not db.query(Comments).filter(Comments.id == comment_id).first():
        raise HTTPException(status_code=404, detail="Comment not found")
    
    reply_model = CommentsReply(content=comment.content, comment_id=comment_id, owner_id=user.get('id'))
    
    db.add(reply_model)
    db.commit()
    return {"message": "Reply to a Comment added successfully!"}

@router.put('/comment/{comment_id}')
def edit_comment(user: user_dependency, db: db_dependency, comment: CommentRequest, comment_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    comment_model = db.query(Comments).filter(Comments.id == comment_id).first() #Fetch the specific comment from the database

    if comment_model is None:
        raise HTTPException(status_code=404, detail="Comment not found")
        
    if comment_model.owner_id != user.get('id'): #Ensuring the logged-in user is the owner of this comment
        raise HTTPException(status_code=403, detail="Forbidden: You can only edit your own comments")
        
    comment_model.content = comment.content #Updating the content and save it to the database
    db.commit()
    return {"message": "Comment updated successfully!"}

@router.put('/commentreply/{reply_id}')
def edit_comment_reply(user: user_dependency, db: db_dependency, reply: CommentRequest, reply_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    reply_model = db.query(CommentsReply).filter(CommentsReply.id == reply_id).first() 

    if reply_model is None:
        raise HTTPException(status_code=404, detail="Reply not found")
        
    if reply_model.owner_id != user.get('id'): 
        raise HTTPException(status_code=403, detail="Forbidden: You can only edit your own replies")
        
    reply_model.content = reply.content 
    db.commit()
    
    return {"message": "Reply updated successfully!"}