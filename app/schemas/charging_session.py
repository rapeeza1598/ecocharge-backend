import datetime
from typing import Optional
from pydantic import BaseModel


class ChargingSession(BaseModel):
    id: str
    userId: str
    boothId: str


class createChargingSession(BaseModel):
    boothId: str


class updateChargingSession(BaseModel):
    powerUsed: Optional[float]

class stopChargingSession(BaseModel):
    endTime: Optional[datetime.datetime] = datetime.datetime.now()
    status: Optional[str] = "completed"