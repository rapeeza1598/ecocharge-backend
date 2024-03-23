from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.crud import charging_booth
from app.database import get_db
from app.schemas.charging_booth import ChargingBooth, createChargingBooth
from app.schemas.user import User

router = APIRouter(
    prefix="/charging_booth",
    tags=["Charging Booth"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def read_charging_booths():
    return {"message": "Read charging booths"}


@router.get("/{station_id}", response_model=List[ChargingBooth])
async def read_charging_booth_in_station(
    station_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return charging_booth.get_charging_booth_by_station_id(db, station_id)


@router.post("/charging_booth")
async def create_charging_booth(
    station_id: str,
    create_charging_booth: createChargingBooth,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if charging_booth.add_charging_booth(
        db, create_charging_booth.booth_name, station_id
    ):
        return {"message": "Charging Booth added successfully"}
    else:
        raise HTTPException(status_code=400, detail="Charging Booth not added")


@router.put("/{booth_id}/status")
async def update_charging_booth_status(
    booth_id: str,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if charging_booth.update_charging_booth_status(db, booth_id, status):
        return {"message": "Charging Booth status updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="Charging Booth status not updated")


@router.put("/{booth_id}/rate")
async def update_charging_booth_rate(
    booth_id: str,
    charging_rate: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if charging_booth.update_charging_booth_rate(db, booth_id, charging_rate):
        return {"message": "Charging Booth rate updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="Charging Booth rate not updated")


@router.put("/{booth_id}")
async def update_charging_booth(
    booth_id: str,
    booth_name: str,
    station_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if charging_booth.update_charging_booth(db, booth_id, booth_name, station_id):
        return {"message": "Charging Booth updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="Charging Booth not updated")


@router.delete("/{booth_id}")
async def delete_charging_booth(
    booth_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if charging_booth.delete_charging_booth(db, booth_id):
        return {"message": "Charging Booth deleted successfully"}
    else:
        raise HTTPException(status_code=400, detail="Charging Booth not deleted")
