from typing import List
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine

# テーブルの作成
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# DBセッションの作成
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# @app.get("/")
# async def index():
#     return {"message": "Success"}
# Read
@app.get("/users", response_model=List[schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/rooms", response_model=List[schemas.Room])
async def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rooms = crud.get_rooms(db, skip=skip, limit=limit)
    return rooms

@app.get("/bookings", response_model=List[schemas.Booking])
async def read_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bookings = crud.get_bookings(db, skip=skip, limit=limit)
    return bookings

#ユーザー詳細ページ
@app.get("/user/{user_id}", response_model=schemas.User)
async def read_user_detail(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_detail(db, user_id=user_id)
    return user

@app.post("/users")
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@app.post("/rooms", response_model=schemas.Room)
async def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    return crud.create_room(db=db, room=room)

@app.post("/bookings", response_model=schemas.Booking)
async def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    return crud.create_booking(db=db, booking=booking)

@app.post("/user/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.update_user(user_id=user_id, user=user, db=db)

@app.get("/room/delete/{room_id}")
async def delete_room(room_id: int, db: Session = Depends(get_db)):
    return crud.delete_room(room_id=room_id, db=db)

@app.post("/login", response_model=schemas.User)
async def login_user(user: schemas.Userlogin, db: Session = Depends(get_db)):
    return crud.login_user(user=user, db=db)