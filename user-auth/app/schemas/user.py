from pydantic import BaseModel, EmailStr
from enum import Enum

class Role(str, Enum):
    user = "user"
    admin = "admin"

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RegisterUserRequest(BaseModel):
    full_name: str
    department: str
    username: str
    password: str
    email: EmailStr
    role: Role

    