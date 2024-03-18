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

class createTransaction(BaseModel):
    userId: UUID
    amount: float
    transactionType: str
    description: str