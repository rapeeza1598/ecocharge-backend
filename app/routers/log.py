from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.crud.logs import (
    delete_log_by_time,
    get_logs,
    get_logs_by_charging_booth_id,
    get_logs_by_station_id,
    get_logs_by_user_id,
)
from app.database import get_db
from app.schemas.log import DeleteLogs
from app.schemas.user import User

router = APIRouter(
    prefix="/log",
    tags=["Log"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def read_logs(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if logs := get_logs(db=db, skip=skip, limit=limit):
        return logs
    raise HTTPException(status_code=400, detail="Logs not found")


@router.get("/{user_id}")
async def read_logs_by_user_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if logs := get_logs_by_user_id(db, user_id):
        return logs
    raise HTTPException(status_code=400, detail="Logs not found")


@router.get("/{station_id}")
async def read_logs_by_station_id(
    station_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if logs := get_logs_by_station_id(db, station_id):
        return logs
    raise HTTPException(status_code=400, detail="Logs not found")


@router.get("/{charging_booth_id}")
async def read_logs_by_charging_booth_id(
    charging_booth_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if logs := get_logs_by_charging_booth_id(db, charging_booth_id):
        return logs
    raise HTTPException(status_code=400, detail="Logs not found")


@router.delete("/")
async def delete_log(
    delete_time: DeleteLogs,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if delete_log_by_time(db, delete_time.start_date, delete_time.end_date):
        return {"message": "Logs deleted successfully"}
    raise HTTPException(status_code=400, detail="Logs not deleted")
