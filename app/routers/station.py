import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from sqlalchemy.orm import Session

from app.crud.charging_session import get_charging_session_by_station_id
from app.crud import station
from app.crud.logs import create_log_info
from app.database import get_db
from app.schemas.station import Station, createStation, updateStation
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
        user_activity = f"User {current_user.email} created station {station_new.name}"
        create_log_info(db, str(current_user.id), user_activity,type_log="station")
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
        user_activity = f"User {current_user.email} read station {station_id}"
        create_log_info(db, str(current_user.id), user_activity,station_id=station_id,type_log="station")
        return stations
    else:
        raise HTTPException(status_code=404, detail="Station not found")


@router.put("/{station_id}", response_model=Station)
async def update_station(
    station_id: str,
    station_update: updateStation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if db_station := station.update_station(db, station_id, station_update):
        user_activity = (
            f"User {current_user.email} updated station {station_update.name}"
        )
        create_log_info(db, str(current_user.id), user_activity,station_id=station_id,type_log="station")
        return db_station
    else:
        raise HTTPException(status_code=400, detail="Station not updated")


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
        user_activity = f"User {current_user.email} deleted station {station_id}"
        create_log_info(db, str(current_user.id), user_activity,station_id=station_id,type_log="station")
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


@router.get("/{station_id}/admins")
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


@router.get("/{station_id}/booths/status")
async def get_station_booths_status(
    station_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if current_user.role not in ["superadmin", "stationadmin"]:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return station.get_station_booths_status(db, station_id)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Station Booths status not found"
        ) from e
