from fastapi import FastAPI, status, Depends, HTTPException
from typing import Annotated
from models import Users, UpdateUserRequest, Shanyrak, CreateShanyrakRequest, CreateCommentRequest, Comment
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

@app.get("/shanyraks/{shanyrak_id}", status_code=status.HTTP_200_OK)
async def get_shanyrak_details(
    shanyrak_id: int,
    user: user_dependency,
    db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    shanyrak = db.query(Shanyrak).filter(Shanyrak.id == shanyrak_id).first()
    if not shanyrak:
        raise HTTPException(status_code=404, detail='Shanyrak not found')

    if shanyrak.owner_id != user['id']:
        raise HTTPException(status_code=403, detail='Unauthorized')

    return {
        "id": shanyrak.id,
        "type": shanyrak.type,
        "price": shanyrak.price,
        "address": shanyrak.address,
        "area": shanyrak.area,
        "rooms_count": shanyrak.rooms_count,
        "description": shanyrak.description,
        "user_id": shanyrak.owner_id
    }



@app.patch("/shanyraks/{shanyrak_id}", status_code=status.HTTP_200_OK)
async def update_shanyrak(
    shanyrak_id: int,
    shanyrak_data: CreateShanyrakRequest,
    user: user_dependency,
    db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    shanyrak = db.query(Shanyrak).filter(Shanyrak.id == shanyrak_id).first()
    if not shanyrak:
        raise HTTPException(status_code=404, detail='Shanyrak not found')

    # Checks if the user owns the shanyrak
    if shanyrak.owner_id != user['id']:
        raise HTTPException(status_code=403, detail='Unauthorized')

    # Updates the shanyrak data
    shanyrak.type = shanyrak_data.type
    shanyrak.price = shanyrak_data.price
    shanyrak.address = shanyrak_data.address
    shanyrak.area = shanyrak_data.area
    shanyrak.rooms_count = shanyrak_data.rooms_count
    shanyrak.description = shanyrak_data.description

    db.commit()

    return {"message": "Shanyrak updated successfully"}

@app.delete("/shanyraks/{shanyrak_id}", status_code=status.HTTP_200_OK)
async def delete_shanyrak(
    shanyrak_id: int,
    user: user_dependency,
    db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    shanyrak = db.query(Shanyrak).filter(Shanyrak.id == shanyrak_id).first()
    if not shanyrak:
        raise HTTPException(status_code=404, detail='Shanyrak not found')

    # Checks if the user owns the shanyrak
    if shanyrak.owner_id != user['id']:
        raise HTTPException(status_code=403, detail='Unauthorized')

    db.delete(shanyrak)
    db.commit()

    return {"message": "Shanyrak deleted successfully"}



@app.post("/shanyraks/{shanyrak_id}/comments", status_code=status.HTTP_200_OK)
async def create_comment(
    shanyrak_id: int,
    comment_data: CreateCommentRequest,
    user: user_dependency,
    db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    shanyrak = db.query(Shanyrak).filter(Shanyrak.id == shanyrak_id).first()
    if not shanyrak:
        raise HTTPException(status_code=404, detail='Shanyrak not found')

    # Create the comment
    comment = Comment(
        content=comment_data.content,
        shanyrak_id=shanyrak_id,
        user_id=user['id']
    )

    db.add(comment)
    db.commit()

    return {"message": "Comment added successfully"}
