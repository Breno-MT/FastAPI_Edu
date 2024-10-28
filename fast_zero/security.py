from datetime import datetime, timedelta
from pwdlib import PasswordHash
from zoneinfo import ZoneInfo
from http import HTTPStatus
from jwt import decode, encode
from jwt.exceptions import PyJWTError
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fast_zero.database import get_session
from fast_zero.models import User

SECRET_KEY='from-env' # Will be removed from here, relax ;)
ALGORITHM='HS256'
ACCESS_TOKEN_EXPIRE_MINUTES=30

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp': expire})

    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme)
    ):

    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise credentials_exception

    except PyJWTError:
        raise credentials_exception

    user_db = session.scalar(
        select(User).where(User.username == username)
    )

    if not user_db:
        raise credentials_exception
    
    return user_db