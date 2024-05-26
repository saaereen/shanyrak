from database import Base
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone = Column(String)
    name = Column(String)
    city = Column(String)
    comments = relationship("Comment", back_populates="owner")

class CreateUserRequest(BaseModel):
    username: str
    password: str
    phone: str
    name: str
    city: str

class Token(BaseModel):
    access_token: str
    token_type: str   
    
class UpdateUserRequest(BaseModel):
    username: str | None = None
    phone: str | None = None
    name: str | None = None
    city: str | None = None
    

class Shanyrak(Base):
    __tablename__ = 'shanyraks'
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    area = Column(String, nullable=False)
    rooms_count = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))

    comments = relationship("Comment", back_populates="shanyrak")

class CreateShanyrakRequest(BaseModel):
    type: str
    price: float
    address: str
    area: str
    rooms_count: int
    description: str    


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    shanyrak_id = Column(Integer, ForeignKey('shanyraks.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship('Users', back_populates='comments')
    shanyrak = relationship('Shanyrak', back_populates='comments')

class CreateCommentRequest(BaseModel):
    content: str    

class UpdateCommentResponse(BaseModel):
    message: str
    original_content: str   