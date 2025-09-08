from pydantic import BaseModel, EmailStr, constr
from enum import Enum

class Role(str, Enum):
    user = "user"
    admin = "admin"

class LoginRequest(BaseModel):
    username: constr(max_length=10)
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    first_login: bool = False

class RegisterUserRequest(BaseModel):
    full_name: str
    department: str
    username: constr(max_length=10)
    password: str
    email: EmailStr
    role: Role

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

    