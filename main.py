from fastapi import FastAPI, status, Depends, HTTPException
from typing import Annotated
from models import Users, UpdateUserRequest, Shanyrak, CreateShanyrakRequest
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import auth
import models
from auth import get_current_user


app = FastAPI()
app.include_router(auth.router)
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]



@app.get("/", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return {"User" : "user"}

@app.post("/shanyraks/", status_code=status.HTTP_200_OK)
async def create_shanyrak(
    shanyrak_request: CreateShanyrakRequest,
    user: user_dependency,
    db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    shanyrak_model = Shanyrak(
        type=shanyrak_request.type,
        price=shanyrak_request.price,
        address=shanyrak_request.address,
        area=shanyrak_request.area,
        rooms_count=shanyrak_request.rooms_count,
        description=shanyrak_request.description,
        owner_id=user['id']
    )

    db.add(shanyrak_model)
    db.commit()
    db.refresh(shanyrak_model)

    return {"id": shanyrak_model.id}