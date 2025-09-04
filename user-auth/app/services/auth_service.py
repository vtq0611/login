from sqlalchemy.orm import Session
from app.models.user import User
from fastapi import HTTPException
from fastapi.params import Depends
from jose import jwt, JWTError
from app.database import SessionLocal
from fastapi.security import OAuth2PasswordBearer
import hashlib
import os
import logging
from contextlib import contextmanager
from typing import Optional

SECRET_KEY = os.getenv("JWT_SECRET", "defaultsecret")
ALGORITHM = "HS256"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_md5(password: str):
    return hashlib.md5(password.encode()).hexdigest()

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    try:
        hashed_password = hash_md5(password)
        user = db.query(User).filter(
            User.username == username, 
            User.hashed_password == hashed_password
        ).first()
        if not user:
            logger.warning(f"Authentication failed for user: {username}")
            return None
        return user
    except Exception as e:
        logger.error(f"Database error during authentication: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def create_access_token(user: User):
    payload = {
        "sub": user.username,
        "role": user.role,
        "email": user.email
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm = ALGORITHM)
    return token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")##
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        logger.debug(f"Decoding token: {token[:10]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            logger.warning("Token payload missing 'sub' claim")
            raise HTTPException(status_code=401, detail="Invalid token")

        with get_db() as db:
            user = db.query(User).filter(User.username == username).first()
            if user is None:
                logger.warning(f"User not found: {username}")
                raise HTTPException(status_code=401, detail="User not found")
            return user

    except JWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")