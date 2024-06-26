from fastapi import HTTPException, APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import update
from starlette import status
from database import SessionLocal
from models import UpdateUserRequest, Users, CreateUserRequest, Token
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Annotated
from pydantic import BaseModel



router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = 'Y32YeEA5Ygu8O1zL5oN1Vdr5+dOSBAdj2OqRk0a3erQ'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/users/login')

 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]    



def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()   
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')




@router.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(
    create_user_request: CreateUserRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(db_dependency)
):
    if current_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create a new user while logged in."
        )
    create_user_model = Users(
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        phone=create_user_request.phone,  
        city=create_user_request.city,                  
        name=create_user_request.name 
    )
    db.add(create_user_model)
    db.commit()

    return {"message": "User created successfully"}

@router.post("/users/login", response_model=Token)  
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}




@router.patch("/users/me")
async def update_user(user_data: UpdateUserRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user['id']
    db_user = db.query(Users).filter(Users.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in user_data:
        setattr(db_user, field, value)
    
    db.commit()
    return {"msg": "User updated successfully"}


@router.get("/users/me")
async def get_user_info(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user['id']
    db_user = db.query(Users).filter(Users.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": db_user.id,
        "username": db_user.username,
        "phone": db_user.phone,
        "name": db_user.name,
        "city": db_user.city
    }


    