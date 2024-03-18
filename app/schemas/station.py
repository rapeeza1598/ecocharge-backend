import datetime
from pydantic import BaseModel
from typing import List, Optional


class Station(BaseModel):
    id: str
    name: str
    location: List[float]
    created_at: datetime.datetime


class createStation(BaseModel):
    name: str
    location: List[float] = [0.00, 0.00]


class updateStation(BaseModel):
    name: Optional[str]
    location: Optional[List[float]]
