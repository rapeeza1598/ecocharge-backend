import datetime
from uuid import UUID
from pydantic import BaseModel
from typing import List, Optional

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

class updateUser(BaseModel):
    firstName: Optional[str]
    lastName: Optional[str]
    phoneNumber: Optional[str]

class updateUserBySuperAdmin(BaseModel):
    firstName: Optional[str]
    lastName: Optional[str]
    phoneNumber: Optional[str]
    email: Optional[str]
    role: Optional[str]
    is_active: Optional[bool]

class updatePassword(BaseModel):
    oldPassword: str
    password: str
    confirmPassword: str

class updatePasswordBySuperAdmin(BaseModel):
    password: str
    confirmPassword: str

class Transaction(BaseModel):
    id: UUID
    userId: str
    amount: float
    transactionType: str
    description: str

class createTransaction(BaseModel):
    userId: UUID
    amount: float
    transactionType: str
    description: str

class Station(BaseModel):
    id: UUID
    name: str
    location: List[float]
    created_at: datetime.datetime

class createStation(BaseModel):
    name: str
    location: List[float] = [0.0, 0.0]

class updateStation(BaseModel):
    name: Optional[str]
    location: Optional[List[float]]

class StationAdmin(BaseModel):
    id: UUID
    userId: UUID
    stationId: UUID
    created_at: datetime.datetime

class createStationAdmin(BaseModel):
    userId: UUID
    stationId: UUID

class updateStationAdmin(BaseModel):
    userId: Optional[UUID]
    stationId: Optional[UUID]

class ChargingSession(BaseModel):
    id: UUID
    userId: UUID
    stationId: UUID
    powerUsed: float
    startTime: datetime.datetime
    endTime: datetime.datetime
    created_at: datetime.datetime
    status: str

class createChargingSession(BaseModel):
    userId: UUID
    stationId: UUID
    powerUsed: float
    startTime: datetime.datetime
    endTime: datetime.datetime
    status: str

class updateChargingSession(BaseModel):
    powerUsed: Optional[float]
    endTime: Optional[datetime.datetime]
    status: Optional[str]

class TokenData(BaseModel):
    email: str | None = None