import datetime
from uuid import UUID
from pydantic import BaseModel


class Transaction(BaseModel):
    id: UUID
    userId: str
    amount: float
    transactionType: str
    description: str
    created_at: datetime.datetime


class createTransaction(BaseModel):
    userId: str
    amount: float
    transactionType: str
    description: str

class responseTransaction(BaseModel):
    id: UUID
    userId: str
    firstName: str
    lastName: str
    email: str
    amount: float
    transactionType: str
    description: str
    created_at: datetime.datetime