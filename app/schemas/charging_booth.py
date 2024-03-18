import datetime
from pydantic import BaseModel


class ChargingBooth(BaseModel):
    booth_id: str
    booth_name: str
    station_id: str
    status: str
    charging_rate: float
    created_at: datetime.datetime
    updated_at: datetime.datetime

class createChargingBooth(BaseModel):
    booth_name: str

class updateChargingBooth(BaseModel):
    booth_name: str
    station_id: str
    updated_at: datetime.datetime

class updateChargingBoothStatus(BaseModel):
    status: str

class updateChargingBoothRate(BaseModel):
    charging_rate: float
