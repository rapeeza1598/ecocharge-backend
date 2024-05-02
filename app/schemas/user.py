import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class Login(BaseModel):
    username: str
    password: str


class User(BaseModel):
    id: UUID
    firstName: str
    lastName: str
    balance: float
    email: str
    phoneNumber: str
    role: str
    is_active: bool
    is_verify: bool
    created_at: datetime.datetime


class createUser(BaseModel):
    firstName: str
    lastName: str
    email: str
    phoneNumber: str
    password: str
    confirmPassword: str


class createUserBySuperAdmin(BaseModel):
    firstName: str
    lastName: str
    email: str
    phoneNumber: str
    password: str
    confirmPassword: str
    role: str


class updateUser(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    phoneNumber: Optional[str] = None


class updateUserBySuperAdmin(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    phoneNumber: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class changePassword(BaseModel):
    oldPassword: str
    password: str
    confirm_password: str


class changePasswordBySuperAdmin(BaseModel):
    password: str
    confirmPassword: str


class TokenData(BaseModel):
    email: str | None = None

class EmailRequest(BaseModel):
    email: str