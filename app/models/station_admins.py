import datetime
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String
from app.database import Base


class StationAdmin(Base):
    __tablename__ = "station_admins"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    stationId = Column(String, ForeignKey("stations.id"))
    created_at = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, userId, stationId):
        self.id = str(uuid.uuid4())
        self.userId = userId
        self.stationId = stationId
        self.created_at = datetime.datetime.now()
