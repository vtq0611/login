from fastapi import APIRouter, Depends, HTTPException 
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, LoginResponse, RegisterUserRequest, Role, ChangePasswordRequest
from app.services.auth_service import authenticate_user, create_access_token, get_current_user, hash_md5
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token(user)
    return LoginResponse(access_token=access_token, first_login=user.first_login)


@router.post("/register", tags=["Admin"])
def register_user(
    new_user: RegisterUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != Role.admin:
        raise HTTPException(status_code=403, detail="Bạn không có quyền thực hiện thao tác này")

    # Kiểm tra trùng username hoặc email
    if len(new_user.username) != 10:
        raise HTTPException(status_code=400, detail="Số điện thoại phải đúng 10 ký tự")
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

@router.put("/change-password", tags=["auth"])
def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # kiểm tra mật khẩu cũ
    if current_user.hashed_password != hash_md5(req.old_password):
        raise HTTPException(status_code=400, detail="Mật khẩu không đúng")

    # kiểm tra mật khẩu mới không được trùng mật khẩu hiện tại
    if current_user.hashed_password == hash_md5(req.new_password):
        raise HTTPException(status_code=400, detail="Mật khẩu mới phải khác mật khẩu hiện tại")

    if current_user.first_login:
        current_user.first_login = False

    # cập nhật mật khẩu mới
    current_user.hashed_password = hash_md5(req.new_password)
    db.add(current_user)
    db.commit()

    return {"message": "Đổi mật khẩu thành công!"}



