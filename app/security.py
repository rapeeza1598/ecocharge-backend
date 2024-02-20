import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from app import crud,schemas
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db, email: str, password: str):
    user = crud.get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: datetime.timedelta = datetime.timedelta()):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))) # type: ignore
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, f"{os.getenv('SECRET_KEY')}", algorithm=f"{os.getenv('ALGORITHM')}")
    return encoded_jwt

def get_current_user(db: Depends = Depends(crud.get_db), token: str = Depends(oauth2_scheme)): # type: ignore
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, f"{os.getenv('SECRET_KEY')}", algorithms=[f"{os.getenv('ALGORITHM')}"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user