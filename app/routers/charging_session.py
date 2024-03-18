from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.station import get_station_by_id
from app.crud.user import get_user_by_id
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

@router.post("/")
async def create_charging_session(
    charging_session: createChargingSession,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = get_user_by_id(db, charging_session.userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    station = get_station_by_id(db, charging_session.stationId)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    if user.balance < 0: # type: ignore
        raise HTTPException(status_code=400, detail="Insufficient balance")
    if db_charging_session := create_charging_session(db, charging_session): # type: ignore
        return db_charging_session
    else:
        raise HTTPException(status_code=400, detail="Charging session not created")

@router.put("/{charging_session_id}")
async def stop_charging_session(
    charging_session_id: str,
    charging_session: updateChargingSession,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return stop_charging_session(db, charging_session_id, charging_session) # type: ignore

