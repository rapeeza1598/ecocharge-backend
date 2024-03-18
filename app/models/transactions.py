import datetime
import uuid
from sqlalchemy import DECIMAL, Column, DateTime, ForeignKey, String
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    userId = Column(String, ForeignKey("users.id"))
    amount = Column(DECIMAL)
    transactionType = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, userId, amount, transactionType, description):
        self.id = str(uuid.uuid4())
        self.userId = userId
        self.amount = amount
        self.transactionType = transactionType
        self.description = description
        self.created_at = datetime.datetime.now()
