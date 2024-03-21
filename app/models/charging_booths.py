import datetime
import uuid
from sqlalchemy import DECIMAL, Column, DateTime, ForeignKey, String
from app.database import Base


class ChargingBooth(Base):
    __tablename__ = "charging_booth"

    booth_id = Column(String, primary_key=True, index=True)
    booth_name = Column(String,unique=True, default="Charging Booth")
    station_id = Column(String, ForeignKey("stations.id"))
    status = Column(String, default="offline")
    charging_rate = Column(DECIMAL, default=0.00)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, booth_name, station_id):
        self.booth_id = str(uuid.uuid4())
        self.booth_name = booth_name
        self.station_id = station_id
        self.status = "offline"
        self.charging_rate = 0.00
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
