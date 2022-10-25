from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app import models, schemas
from app.config import settings
from .database import get_db
from sqlalchemy.orm import Session

SECRET_KEY = settings.jwt_secret
ALGORITHM = settings.jwt_algorithm
JWT_EXPIRES_IN = settings.jwt_expires_in
oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRES_IN)
    to_encode.update({"exp": expire, "iat": datetime.now()})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str, credentials_exception):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception
        return id
    except JWTError:
        raise credentials_exception


def get_current_user(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    id = verify_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == id).first()
    return user
