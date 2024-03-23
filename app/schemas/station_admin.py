import datetime
from pydantic import BaseModel


class StationAdmin(BaseModel):
    id: str
    station_id: str
    userId: str
    created_at: datetime.datetime


class createStationAdmin(BaseModel):
    station_id: str
    admin_id: str


class updateStationAdmin(BaseModel):
    station_id: str
    admin_id: str


class deleteStationAdmin(BaseModel):
    station_id: str
    admin_id: str


class getStationAdmin(BaseModel):
    station_id: str
    admin_id: str
    created_at: datetime.datetime
