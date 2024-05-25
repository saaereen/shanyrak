from database import Base
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String

class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone = Column(String)
    name = Column(String)
    city = Column(String)
    
class UpdateUserRequest(BaseModel):
    username: str | None = None
    phone: str | None = None
    name: str | None = None
    city: str | None = None