import datetime
import uuid
from sqlalchemy import DECIMAL, Column, DateTime, ForeignKey, String
from app.database import Base


class ChargingSession(Base):
    __tablename__ = "charging_sessions"

    id = Column(String, primary_key=True, index=True)
    userId = Column(String, ForeignKey("users.id"))
    stationId = Column(String, ForeignKey("stations.id"))
    powerUsed = Column(DECIMAL, default=0.00)
    startTime = Column(DateTime, default=datetime.datetime.now())
    endTime = Column(DateTime, default=datetime.datetime.now())
    status = Column(String, default="in-progress")

    def __init__(self, userId, stationId, powerUsed, endTime, status):
        self.id = str(uuid.uuid4())
        self.userId = userId
        self.stationId = stationId
        self.powerUsed = powerUsed
        self.startTime = datetime.datetime.now()
        self.endTime = endTime
        self.status = status
