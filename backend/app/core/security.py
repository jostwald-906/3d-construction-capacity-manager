from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def create_access_token(sub: str, role: str, expires_minutes: int = 60) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {"sub": sub, "role": role, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
