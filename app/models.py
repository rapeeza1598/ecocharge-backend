import datetime
from venv import create
from sqlalchemy import Column, ForeignKey, String,Boolean,DateTime,ARRAY,DECIMAL
from app.database import Base
import uuid

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
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
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

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    userId = Column(String,ForeignKey('users.id'))
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

class Station(Base):
    __tablename__ = "stations"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    location = Column(ARRAY(DECIMAL), default=[0.0, 0.0])
    status = Column(String, default="online")
    created_at = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, name, location):
        self.id = str(uuid.uuid4())
        self.name = name
        self.location = location
        self.status = "online"
        self.created_at = datetime.datetime.now()

class StationAdmin(Base):
    __tablename__ = "station_admins"

    id = Column(String, primary_key=True, index=True)
    userId = Column(String,ForeignKey('users.id'),unique=True, index=True)
    stationId = Column(String,ForeignKey('stations.id'))
    created_at = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, userId, stationId):
        self.id = str(uuid.uuid4())
        self.userId = userId
        self.stationId = stationId
        self.created_at = datetime.datetime.now()

class ChargingSession(Base):
    __tablename__ = "charging_sessions"

    id = Column(String, primary_key=True, index=True)
    userId = Column(String,ForeignKey('users.id'))
    stationId = Column(String,ForeignKey('stations.id'))
    powerUsed = Column(DECIMAL, default=0.00)
    startTime = Column(DateTime, default=datetime.datetime.now())
    endTime = Column(DateTime, default=datetime.datetime.now())
    created_at = Column(DateTime, default=datetime.datetime.now())
    status = Column(String, default="in-progress")

    def __init__(self, userId, stationId, powerUsed, startTime, endTime, status):
        self.id = str(uuid.uuid4())
        self.userId = userId
        self.stationId = stationId
        self.powerUsed = powerUsed
        self.startTime = startTime
        self.endTime = endTime
        self.status = status
        self.created_at = datetime.datetime.now()