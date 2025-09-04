from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base
from enum import Enum

class Role(str, Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True) #sđt
    hashed_password = Column(String)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    department = Column(String)
    role = Column(String, default="user") #user, admin
    first_login = Column(Boolean, default=True)