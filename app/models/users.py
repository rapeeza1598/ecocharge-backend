import datetime
from app.database import Base
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, DECIMAL


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    firstName = Column(String)
    lastName = Column(String)
    balance = Column(DECIMAL, default=0.00)
    email = Column(String, unique=True, index=True)
    phoneNumber = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=False)
    is_verify = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, firstName, lastName, email, phoneNumber, hashed_password, role):
        self.id = str(uuid.uuid4())
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.phoneNumber = phoneNumber
        self.hashed_password = hashed_password
        self.role = role
        self.created_at = datetime.datetime.now()
