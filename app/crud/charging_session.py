from sqlalchemy.orm import Session

from app.models.charging_sessions import ChargingSession
from app.schemas.charging_session import createChargingSession, updateChargingSession


def create_charging_session(
    db: Session, charging_session: createChargingSession
):
    db_charging_session = ChargingSession(**charging_session.dict())
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
        .filter(ChargingSession.userId == user_id) # type: ignore
        .all()
    )


def get_charging_session_by_id(db: Session, charging_session_id: str):
    return (
        db.query(ChargingSession)
        .filter(ChargingSession.id == charging_session_id) # type: ignore
        .first()
    )


def get_charging_session_by_station_id(db: Session, station_id: str):
    return (
        db.query(ChargingSession)
        .filter(ChargingSession.stationId == station_id) # type: ignore
        .all()
    )


def update_charging_session(
    db: Session,
    charging_session_id: str,
    charging_session: updateChargingSession,
):
    db_charging_session = (
        db.query(ChargingSession)
        .filter(ChargingSession.id == charging_session_id) # type: ignore
        .first()
    )
    db.query(ChargingSession).filter(
        ChargingSession.id == charging_session_id # type: ignore
    ).update(charging_session) # type: ignore
    try:
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
        .filter(ChargingSession.id == charging_session_id) # type: ignore
        .first()
    )
    db.query(ChargingSession).filter(
        ChargingSession.id == charging_session_id # type: ignore
    ).update(charging_session) # type: ignore
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
    charging_session: updateChargingSession,
):
    db_charging_session = (
        db.query(ChargingSession)
        .filter(ChargingSession.id == charging_session_id) # type: ignore
        .first()
    )
    # status = "completed" if charging_session.status == "completed" else "stopped"
    setattr(db_charging_session, "status", "completed")
    setattr(db_charging_session, "endTime", charging_session.endTime)
    setattr(db_charging_session, "powerUsed", charging_session.powerUsed)
    try:
        db.commit()
        db.refresh(db_charging_session)
    except Exception as e:
        print(e)
        return None
    return db_charging_session
