from database import Base
from sqlalchemy import Column, Integer, String, Boolean,ForeignKey
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ = 'users' 

    id = Column(Integer, primary_key=True, index=True) 
    email = Column(String, unique=True, index=True) 
    username = Column(String, unique=True, index=True) 
    first_name = Column(String) 
    last_name = Column(String) 
    hashed_password = Column(String) 
    is_active = Column(Boolean, default=True) 
    role = Column(String) 

class Posts(Base):
    __tablename__ = 'posts' 

    id = Column(Integer, primary_key=True, index=True) 
    title = Column(String, index=True) 
    description = Column(String, index=True) 
    owner_id = Column(Integer, ForeignKey("users.id"))
    image_url = Column(String, nullable=True)
    comments = relationship("Comments")

class Likes(Base): 
    __tablename__= 'likes'

    id = Column(Integer, primary_key=True, index=True) 
    post_id= Column(Integer, ForeignKey("posts.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

class Comments(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner=relationship("Users")
    replies = relationship("CommentsReply")

class CommentsReply(Base):
    __tablename__ = 'comments_reply'
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("Users")