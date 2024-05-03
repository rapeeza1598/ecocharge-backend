import datetime
from sqlalchemy import Column, DateTime, String
from app.database import Base


class Token(Base):
    __tablename__ = "tokens"

    token = Column(String, index=True)
    email = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, token, email):
        self.token = token
        self.email = email
        self.timestamp = datetime.datetime.now()
