from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
import models

SECRET_KEY  = "hirefast_secret_key_change_in_production_2024"
ALGORITHM   = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context    = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme  = HTTPBearer()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise exc
    except JWTError:
        raise exc
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise exc
    return user

def require_hr(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role != "HR":
        raise HTTPException(status_code=403, detail="HR access only")
    return current_user

def require_candidate(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role != "Candidate":
        raise HTTPException(status_code=403, detail="Candidate access only")
    return current_user
