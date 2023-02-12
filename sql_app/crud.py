from sqlalchemy.orm import Session
from . import schemas, models
from fastapi import HTTPException
import datetime
import hashlib

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_rooms(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Room).offset(skip).limit(limit).all()

def get_bookings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Booking).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        password=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_room(db: Session, room: schemas.Room):
    db_room = models.Room(
        room_name=room.room_name,
        capacity=room.capacity
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

# 予約登録
def create_booking(db: Session, booking: schemas.Booking):
    db_booked = db.query(models.Booking).\
        filter(models.Booking.room_id == booking.room_id).\
        filter(models.Booking.end_datetime > booking.start_datetime).\
        filter(models.Booking.start_datetime < booking.end_datetime).\
        all()
    # 重複するデータがなければ
    if len(db_booked) == 0:
        db_booking = models.Booking(
            user_id = booking.user_id,
            room_id = booking.room_id,
            booked_num = booking.booked_num,
            start_datetime = booking.start_datetime,
            end_datetime = booking.end_datetime
        )
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking
    else:
        raise HTTPException(status_code=404, detail="Already booked")

def get_user_detail(db: Session, user_id: None):
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def update_user(db: Session, user: schemas.UserCreate, user_id: None):
    db_user = db.query(models.User).filter(models.User.user_id == user_id)
    db_user.update({models.User.username: user.username})
    db.commit()
    first_user = db_user.first()
    return first_user

def delete_room(db: Session, room_id: None):
    db_room = db.query(models.Room).filter(models.Room.room_id == room_id)
    db_room.delete()
    db.commit()
    return {'delete': 'Success'}

def login_user(db: Session, user: schemas.Userlogin):
    password_check_hash = hashlib.sha256(user.password.encode()).hexdigest()
    result = db.query(models.User.user_id, models.User.username).\
        filter(models.User.username == user.username).\
        filter(models.User.password == password_check_hash).first()
    if result:
        return result