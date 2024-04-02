from enum import Enum
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
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


class ChargerStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    CHARGING = "charging"


status = {"station": ChargerStatus.OFFLINE.value}
connections: dict = {}


@router.get("/")
async def read_charging_booths(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    # if current_user.role not in ["superadmin", "stationadmin"]:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    if not charging_booth.get_all_charging_booths(db):
        raise HTTPException(status_code=404, detail="Charging Booths not found")
    return charging_booth.get_all_charging_booths(db)


@router.get("/{booth_id}")
async def read_charging_booth_by_id(
    booth_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not charging_booth.get_charging_booth_by_id(db, booth_id):
        raise HTTPException(status_code=404, detail="Charging Booth not found")
    return charging_booth.get_charging_booth_by_id(db, booth_id)


@router.get("/{station_id}", response_model=List[ChargingBooth])
async def read_charging_booth_in_station(
    station_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # if current_user.role not in ["superadmin", "stationadmin"]:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    return charging_booth.get_charging_booth_by_station_id(db, station_id)


@router.post("/{station_id}")
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


@router.websocket("/ws/{booth_id}/")
async def websocket_endpoint(
    websocket: WebSocket, booth_id: str, db: Session = Depends(get_db)
):
    await websocket.accept()
    try:
        charging_booth.update_charging_booth_status(
            db, booth_id, ChargerStatus.ONLINE.value
        )
        while True:
            data = await websocket.receive_text()
            data_dict = json.loads(data)
            # print(data_dict)
            if data_dict["status"] == "charging":
                status["station"] = ChargerStatus.CHARGING.value
                charging_booth.update_charging_booth_rate(
                    db, booth_id, data_dict["rate"]
                )
            else:
                status["station"] = ChargerStatus.ONLINE.value
                charging_booth.update_charging_booth_rate(db, booth_id, 0.0)
            charging_booth.update_charging_booth_status(db, booth_id, status["station"])
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        status["station"] = ChargerStatus.OFFLINE.value
        print("station is offline")
        charging_booth.update_charging_booth_status(db, booth_id, status["station"])
        # await websocket.close()
