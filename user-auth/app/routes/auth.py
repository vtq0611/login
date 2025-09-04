from fastapi import APIRouter, Depends, HTTPException 
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, LoginResponse, RegisterUserRequest, Role
from app.services.auth_service import authenticate_user, create_access_token, get_current_user, hash_md5

router = APIRouter(prefix="/auth", tags=["auth"])

from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token(user)
    return LoginResponse(access_token=access_token)


@router.post("/register", tags=["Admin"])
def register_user(
    new_user: RegisterUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != Role.admin:
        raise HTTPException(status_code=403, detail="Bạn không có quyền thực hiện thao tác này")

    # Kiểm tra trùng username hoặc email
    if db.query(User).filter(User.username == new_user.username).first():
        raise HTTPException(status_code=400, detail="Username đã tồn tại")
    if db.query(User).filter(User.email == new_user.email).first():
        raise HTTPException(status_code=400, detail="Email đã tồn tại")

    hashed_password = hash_md5(new_user.password)
    user = User(
        full_name=new_user.full_name,
        department=new_user.department,
        username=new_user.username,
        hashed_password=hashed_password,
        email=new_user.email,
        role=new_user.role
    )
    db.add(user)
    db.commit()
    return {"message": f"Tạo tài khoản '{new_user.username}' thành công!"}
