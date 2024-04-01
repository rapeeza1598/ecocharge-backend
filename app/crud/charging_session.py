import datetime
from sqlalchemy.orm import Session

from app.models.charging_sessions import ChargingSession
from app.schemas.charging_session import createChargingSession, stopChargingSession, updateChargingSession


def create_charging_session(db: Session, charging_session: createChargingSession):
    db_charging_session = ChargingSession(
        userId=charging_session.userId,
        booth_id=charging_session.booth_id,
    )
    try:
        db.add(db_charging_session)
        db.commit()
        db.refresh(db_charging_session)
    except Exception as e:
        print(e)
        return None
    return db_charging_session


def get_charging_sessions(db: Session, skip: int = 0, limit: int = 10):
    return db.query(ChargingSession).offset(skip).limit(limit).all()


def get_charging_session_by_user_id(db: Session, user_id: str):
    return (
        db.query(ChargingSession)
        .filter(ChargingSession.userId == user_id)  # type: ignore
        .all()
    )


def get_charging_session_by_id(db: Session, charging_session_id: str):
    return (
        db.query(ChargingSession)
        .filter(ChargingSession.id == charging_session_id)  # type: ignore
        .first()
    )


def get_charging_session_by_station_id(db: Session, station_id: str):
    return (
        db.query(ChargingSession)
        .filter(ChargingSession.stationId == station_id)  # type: ignore
        .all()
    )


def get_charging_session_by_booth_id(db: Session, booth_id: str):
    return (
        db.query(ChargingSession)
        .filter(ChargingSession.booth_id == booth_id)  # type: ignore
        .all()
    )


def update_charging_session(
    db: Session,
    charging_session_id: str,
    lastPower: float,
):
    db_charging_session = (
        db.query(ChargingSession)
        .filter(ChargingSession.id == charging_session_id) # type: ignore
        .first()
    )

    # Check if db_charging_session is None
    if db_charging_session is None:
        print(f"No charging session found with ID {charging_session_id}")
        return None

    try:
        setattr(db_charging_session, "powerUsed", lastPower)
        db.commit()
        db.refresh(db_charging_session)
    except Exception as e:
        print(e)
        return None
    return db_charging_session



def update_charging_session_by_station_id(
    db: Session,
    charging_session_id: str,
    charging_session: updateChargingSession,
):
    db_charging_session = (
        db.query(ChargingSession)
        .filter(ChargingSession.id == charging_session_id)  # type: ignore
        .first()
    )
    setattr(db_charging_session, "powerUsed", charging_session.powerUsed)
    try:
        db.commit()
        db.refresh(db_charging_session)
    except Exception as e:
        print(e)
        return None
    return db_charging_session


def stop_charging_session(
    db: Session,
    charging_session_id: str,
    charging_session: stopChargingSession,
):
    db_charging_session = (
        db.query(ChargingSession)
        .filter(ChargingSession.id == charging_session_id)  # type: ignore
        .first()
    )
    if db_charging_session is None:
        print(f"No charging session found with ID {charging_session_id}")
        return None
    # status = "completed" if charging_session.status == "completed" else "stopped"
    setattr(db_charging_session, "status", "completed")
    setattr(db_charging_session, "endTime", datetime.datetime.now())
    try:
        db.commit()
        db.refresh(db_charging_session)
    except Exception as e:
        print(e)
        return None
    return db_charging_session
