import os
from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import (
    Column, Integer, Text, ForeignKey, DateTime,
    create_engine, func, select, text
)
from sqlalchemy.dialects.postgresql import TSTZRANGE, ExcludeConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from psycopg2.extras import DateTimeTZRange

DB_USER = os.getenv("POSTGRES_USER", "slots_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret_pass")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "slots_db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()
app = FastAPI()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(Text, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    slot = Column(TSTZRANGE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator = relationship("User")
    participants = relationship(
        "Participant",
        back_populates="appointment",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        ExcludeConstraint(('creator_id', '='), ('slot', '&&'), using='gist'),
    )

class Participant(Base):
    __tablename__ = "participants"
    appointment_id = Column(Integer, ForeignKey("appointments.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    email = Column(Text, primary_key=True)
    status = Column(Text, nullable=False, default='pending')
    invited_at = Column(DateTime(timezone=True), server_default=func.now())

    appointment = relationship("Appointment", back_populates="participants")
    user = relationship("User")

class AppointmentIn(BaseModel):
    start_time: datetime = Field(..., example="2025-04-20T13:00:00Z")
    end_time: datetime = Field(..., example="2025-04-20T14:00:00Z")
    participants: List[EmailStr] = Field(
        ..., example=["alice@example.com", "bob@example.com"]
    )

class AppointmentOut(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    participants: List[EmailStr]

    class Config:
        orm_mode = True

@app.on_event("startup")
def on_startup():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist"))
        conn.commit()

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_or_create_user(db, email: str):
    user = db.query(User).filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.add(user)
        db.flush()
    return user

@app.post("/booking/", response_model=AppointmentOut)
def create_appointment(
    data: AppointmentIn,
    db = Depends(get_db),
):
    if data.end_time <= data.start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    creator = get_or_create_user(db, email="creator@example.com")

    ts_range = DateTimeTZRange(data.start_time, data.end_time, '[)')

    appointment = Appointment(creator_id=creator.id, slot=ts_range)
    db.add(appointment)
    db.flush()

    for email in data.participants:
        user = get_or_create_user(db, email)
        part = Participant(
            appointment_id=appointment.id,
            user_id=user.id,
            email=email,
        )
        db.add(part)

    db.commit()
    db.refresh(appointment)

    return AppointmentOut(
        id=appointment.id,
        start_time=data.start_time,
        end_time=data.end_time,
        participants=data.participants,
    )

@app.get("/booking/", response_model=List[AppointmentOut])
def read_appointments(
    email: EmailStr,
    db = Depends(get_db),
):
    stmt = (
        select(Appointment)
        .join(Participant)
        .filter(Participant.email == email)
    )
    results = db.execute(stmt).scalars().all()

    out = []
    for apt in results:
        start, end = apt.slot.lower, apt.slot.upper
        emails = [p.email for p in apt.participants]
        out.append(AppointmentOut(
            id=apt.id,
            start_time=start,
            end_time=end,
            participants=emails,
        ))
    return out
