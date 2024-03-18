import datetime
import uuid
from sqlalchemy import ARRAY, DECIMAL, Column, DateTime, String
from app.database import Base


class Station(Base):
    __tablename__ = "stations"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    location = Column(ARRAY(DECIMAL), default=[0.0, 0.0])
    created_at = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, name, location):
        self.id = str(uuid.uuid4())
        self.name = name
        self.location = location
        self.created_at = datetime.datetime.now()
