import datetime
import uuid
from sqlalchemy import DECIMAL, Boolean, Column, DateTime, ForeignKey, String
from app.database import Base


class Topups(Base):
    __tablename__ = "topups"

    id = Column(String, primary_key=True, index=True)
    userId = Column(String, ForeignKey("users.id"))
    image_base64 = Column(String)
    amount = Column(DECIMAL)
    status_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, userId, image_base64, amount):
        self.id = str(uuid.uuid4())
        self.userId = userId
        self.image_base64 = image_base64
        self.amount = amount