from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.station import get_station_by_id
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


@router.post("/")
async def create_charging_session(
    new_charging_session: createChargingSession,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = get_user_by_id(db, str(current_user.id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    station = get_station_by_id(db, new_charging_session.stationId)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    if user.balance <= 0:  # type: ignore
        raise HTTPException(status_code=400, detail="Insufficient balance")
    if db_charging_session := charging_session.create_charging_session(db, new_charging_session):  # type: ignore
        return db_charging_session
    else:
        raise HTTPException(status_code=400, detail="Charging session not created")


@router.put("/{charging_session_id}")
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
    return {"message": "Charging session Stopped successfully"}
