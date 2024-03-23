import datetime
import uuid
from sqlalchemy import DECIMAL, Column, DateTime, ForeignKey, String
from app.database import Base


class ChargingSession(Base):
    __tablename__ = "charging_sessions"

    id = Column(String, primary_key=True, index=True)
    userId = Column(String, ForeignKey("users.id"))
    booth_id = Column(String, ForeignKey("charging_booth.booth_id"))
    powerUsed = Column(DECIMAL, default=0.00)
    startTime = Column(DateTime, default=datetime.datetime.now())
    endTime = Column(DateTime, default=datetime.datetime.now())
    status = Column(String, default="in-progress")

    def __init__(self, userId, booth_id):
        self.id = str(uuid.uuid4())
        self.userId = userId
        self.booth_id = booth_id
        self.powerUsed = 0.00
        self.startTime = datetime.datetime.now()
        self.endTime = datetime.datetime.now()
        self.status = "in-progress"
