import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from app import database
from app.schemas.user import TokenData
import os
from app.crud.user import get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db, email: str, password: str):
    if user := get_user_by_email(db, email, is_active=True):
        return user if verify_password(password, user.hashed_password) else False
    else:
        return False


def create_access_token(
    data: dict, expires_delta: datetime.timedelta = datetime.timedelta()
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))  # type: ignore
        )
    to_encode["exp"] = expire
    return jwt.encode(
        to_encode,
        f"{os.getenv('SECRET_KEY')}",
        algorithm=f"{os.getenv('ALGORITHM')}",
    )


def get_current_user(db=Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            f"{os.getenv('SECRET_KEY')}",
            algorithms=[f"{os.getenv('ALGORITHM')}"],
        )
        email: str = payload.get("sub")  # type: ignore
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError as e:
        raise credentials_exception from e
    user = get_user_by_email(db, email=token_data.email)  # type: ignore
    if user is None:
        raise credentials_exception
    return user
