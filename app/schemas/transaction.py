import datetime
from pydantic import BaseModel


class Transaction(BaseModel):
    id: str
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
    id: str
    userId: str
    firstName: str
    lastName: str
    email: str
    amount: float
    transactionType: str
    description: str
    created_at: datetime.datetime