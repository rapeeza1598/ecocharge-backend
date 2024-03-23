import datetime
from typing import Optional
from pydantic import BaseModel


class ChargingSession(BaseModel):
    id: str
    userId: str
    booth_id: str


class createChargingSession(BaseModel):
    userId: str
    booth_id: str
    powerUsed: float
    startTime: datetime.datetime
    status: str = "active"


class updateChargingSession(BaseModel):
    powerUsed: Optional[float]
    endTime: Optional[datetime.datetime] = datetime.datetime.now()
    status: Optional[str] = "completed"
