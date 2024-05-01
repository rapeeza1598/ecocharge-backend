import datetime
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String
from app.database import Base

class Logs(Base):
    __tablename__ = "logs"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    station_id = Column(String, ForeignKey("stations.id"), nullable=True)
    booth_id = Column(String, ForeignKey("charging_booth.booth_id"),nullable=True)
    topup_id = Column(String, ForeignKey("topups.id"),nullable=True)
    type_log = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, user_id, message,type_log,station_id=None, charging_booth_id=None, topup_id=None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.station_id = station_id
        self.charging_booth_id = charging_booth_id
        self.topup_id = topup_id
        self.type_log = type_log
        self.message = message
        self.created_at = datetime.datetime.now()
