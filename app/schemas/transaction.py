import datetime
from uuid import UUID
from pydantic import BaseModel
from typing import List, Optional

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