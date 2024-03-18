from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.charging_session import get_charging_session_by_station_id
from app.crud import station
from app.database import get_db
from app.schemas.station import Station, createStation, updateStation
from app.schemas.station_admin import StationAdmin
from app.schemas.user import User
from app.core.security import get_current_user

router = APIRouter(
    prefix="/station",
    tags=["Station"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[Station])
async def read_stations(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return station.get_stations(db, skip=skip, limit=limit)

@router.post("/", response_model=Station)
async def create_new_station(
    station_new: createStation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    if db_station := station.create_station(db, station_new):
        return db_station
    else:
        raise HTTPException(status_code=400, detail="Station not created")
    
@router.get("/{station_id}", response_model=Station)
async def read_station_by_id(
    station_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if stations := station.get_station_by_id(db, station_id):
        return stations
    else:
        raise HTTPException(status_code=404, detail="Station not found")
    
@router.put("/{station_id}", response_model=Station)
async def update_station(
    station_id: str,
    station: updateStation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return update_station(db, station_id, station) # type: ignore

@router.delete("/{station_id}")
async def delete_station_by_superadmin(
    station_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if current_user.role not in ["superadmin", "stationadmin"]:
            raise HTTPException(status_code=401, detail="Unauthorized")
        if not station.get_station_by_id(db, station_id):
            raise HTTPException(status_code=404, detail="Station not found")
        station.delete_station(db, station_id)
        return {"message": "Station deleted successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Station not deleted") from e

@router.get("/{station_id}/power_used")
async def get_station_power_used(
    station_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(
            status_code=401, detail="Not permitted to access this resource"
        )
    charging_sessions = get_charging_session_by_station_id(db, station_id)
    power_used = sum(session.powerUsed for session in charging_sessions)
    return {"stationId": station_id, "powerUsed": power_used}

@router.get("/{station_id}/details")
async def read_station_details(
    station_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(
            status_code=401, detail="Not permitted to access this resource"
        )
    if not station.get_station_by_id(db, station_id):
        raise HTTPException(status_code=404, detail="Station not found")
    charging_sessions = get_charging_session_by_station_id(db, station_id)
    power_used = sum(session.powerUsed for session in charging_sessions)
    return {
        "stationId": station_id,
        "chargingSessions": charging_sessions,
        "powerUsed": power_used,
    }

@router.get("/{station_id}/admins", response_model=List[StationAdmin])
async def read_station_admins(
    station_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if current_user.role not in ["superadmin", "stationadmin"]:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return station.get_station_admins(db, station_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Station Admins not found") from e