from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from src.config.core import settings
import uuid
from fastapi import status, HTTPException
import jwt
from jwt.exceptions import InvalidTokenError

pwd = CryptContext(schemes=['argon2'], deprecated="auto")

def hash(password):
    return pwd.hash(password)

def verify(password, hashed_password):
    return pwd.verify(password, hashed_password)


def Token(user: dict, expire: timedelta = None, refresh: bool = False):
    payload = {}
    payload['user'] = user
    
    if not expire:
        expire = timedelta(minutes=settings.ACCES_TOKEN_EXPIRE)
    if refresh == True:
        expire = timedelta(minutes=settings.REFRESH_TOKEN_TIME)
        
    payload["jti"] = str(uuid.uuid4())
    payload['exp'] = datetime.now(timezone.utc) + expire
    payload["refresh"] = refresh
    
    token = jwt.encode(payload, settings.SECRET_KEY,  algorithm=settings.ALGORITHM)
    return token


def verify_token(token: str):
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No token provided")
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Invalid or token eror",
                            headers={"WWW-Authorization": "Bearer"})
        