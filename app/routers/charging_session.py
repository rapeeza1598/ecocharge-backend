from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session
from app.crud.charging_booth import (
    get_charging_booth_by_id,
    get_charging_booths_by_station_id,
)
from app.crud.user import get_user_by_id
from app.crud import charging_session
from app.database import get_db
from app.schemas.charging_session import createChargingSession, updateChargingSession
from app.schemas.user import User
from app.core.security import get_current_user

router = APIRouter(
    prefix="/charging_sessions",
    tags=["Charging"],
    # default_response_class=Depends(get_current_user),
    responses={404: {"description": "Not found"}},
)

sessions = {}


@router.get("/")
async def get_charging_sessions(db: Session = Depends(get_db)):
    return charging_session.get_charging_sessions(db)


@router.get("/users/{user_id}")
async def get_user_charging_sessions(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not charging_session.get_charging_session_by_user_id(db, user_id):
        raise HTTPException(status_code=404, detail="Charging Session not found")
    return charging_session.get_charging_session_by_user_id(db, user_id)


@router.get("/station/{station_id}")
async def get_station_charging_sessions(
    station_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if charging_booths := get_charging_booths_by_station_id(db, station_id):
        return [
            charging_session.get_charging_session_by_booth_id(db, str(booth.booth_id))
            for booth in charging_booths
        ]
    else:
        raise HTTPException(status_code=404, detail="Station not found")


@router.post("/")
async def create_charging_session(
    new_charging_session: createChargingSession,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = get_user_by_id(db, str(current_user.id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    station = get_charging_booth_by_id(db, new_charging_session.booth_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    if user.balance <= 0:  # type: ignore
        raise HTTPException(status_code=400, detail="Insufficient balance")
    if db_charging_session := charging_session.create_charging_session(db, new_charging_session):  # type: ignore
        sessions[db_charging_session.id]
        print(sessions)
        return db_charging_session


@router.post("/{charging_session_id}")
async def stop_charging_session(
    charging_session_id: str,
    update_charging_session: updateChargingSession,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not charging_session.stop_charging_session(
        db, charging_session_id, update_charging_session
    ):
        raise HTTPException(status_code=400, detail="Charging session not stopped")
    if session := sessions.pop(charging_session_id, None):
        return {"message": "Charging stopped", "session_data": session}
    return {"message": "Charging stopped not found"}


@router.websocket("/ws/charging_session/{charging_session_id}")
async def websocket_endpoint(websocket: WebSocket, charging_session_id: str):
    await websocket.accept()
    while charging_session_id in sessions:
        data = sessions[charging_session_id]
        await websocket.send_json(data)
    await websocket.close()
