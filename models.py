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
    shanyraks = relationship('Shanyrak', back_populates='owner')

    
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

    owner = relationship('Users', back_populates='shanyraks')

class CreateShanyrakRequest(BaseModel):
    type: str
    price: float
    address: str
    area: str
    rooms_count: int
    description: str    