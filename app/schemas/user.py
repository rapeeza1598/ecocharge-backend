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
    is_superuser: bool
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
    firstName: Optional[str]
    lastName: Optional[str]
    phoneNumber: Optional[str]


class updateUserBySuperAdmin(BaseModel):
    firstName: Optional[str]
    lastName: Optional[str]
    phoneNumber: Optional[str]
    role: Optional[str]
    is_active: Optional[bool]


class changePassword(BaseModel):
    oldPassword: str
    password: str
    confirm_password: str


class changePasswordBySuperAdmin(BaseModel):
    password: str
    confirmPassword: str


class TokenData(BaseModel):
    email: str | None = None

class ResetPassword(BaseModel):
    email: str