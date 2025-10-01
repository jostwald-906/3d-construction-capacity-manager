from typing import Annotated
from fastapi import Depends, HTTPException, Header
from jose import JWTError
from sqlalchemy.orm import Session
from app.core.security import decode_token
from app.core.settings import settings
from app.db.session import SessionLocal
from app.models.entities import User

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(authorization: Annotated[str | None, Header()] = None, db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split()[1]
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token decode failed")

def require_role(*roles: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return dependency
