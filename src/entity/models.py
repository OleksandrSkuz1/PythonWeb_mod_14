from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.sql import func
from datetime import datetime

# Створення об'єкта для базового класу
Base = declarative_base()

# Клас для таблиці "contacts"
class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(25), index=True)
    last_name = Column(String(25))
    email = Column(String(50), unique=True, index=True)
    phone = Column(String(50), index=True)
    birthday = Column(Date, index=True)
    additional_data = Column(String(50), index=True)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now(), nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user = relationship("User", backref=backref("contacts", lazy="joined"))

# Клас для таблиці "users"
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    avatar = Column(String(250), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    confirmed = Column(Boolean, default=False, nullable=True)