from sqlalchemy.orm import Session
from app.models.charging_sessions import ChargingSession
from app.models.station_admins import StationAdmin
from app.models.stations import Station
from app.schemas.station import createStation, updateStation
from app.schemas.station_admin import createStationAdmin


def create_station(db: Session, station: createStation):
    db_station = Station(name=station.name, location=station.location)
    try:
        db.add(db_station)
        db.commit()
        db.refresh(db_station)
    except Exception as e:
        print(e)
        return None
    return db_station


def get_stations(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Station).offset(skip).limit(limit).all()


def get_station_by_id(db: Session, station_id: str):
    return db.query(Station).filter(Station.id == station_id).first()  # type: ignore


def update_station(db: Session, station_id: str, station: updateStation):
    db_station = db.query(models.Station).filter(models.Station.id == station_id).first()  # type: ignore
    db.query(models.Station).filter(models.Station.id == station_id).update(station)  # type: ignore
    try:
        db.commit()
        db.refresh(db_station)
    except Exception as e:
        print(e)
        return None
    return db_station


def create_station_admin(db: Session, station_admin: createStationAdmin):
    db_station_admin = StationAdmin(**station_admin.dict())
    try:
        db.add(db_station_admin)
        db.commit()
        db.refresh(db_station_admin)
    except Exception as e:
        print(e)
        return None
    return db_station_admin


def get_station_admins(db: Session, station_id: str = None):  # type: ignore
    if station_id is None:
        return db.query(StationAdmin).all()
    else:
        return (
            db.query(StationAdmin)
            .filter(StationAdmin.stationId == station_id)  # type: ignore
            .join(User, StationAdmin.userId == User.id)  # type: ignore
            .all()
        )


def get_station_admin_by_id(db: Session, station_admin_id: str):
    return db.query(StationAdmin).filter(StationAdmin.id == station_admin_id).first()  # type: ignore


def delete_station(db: Session, station_id: str):
    db.query(Station).filter(Station.id == station_id).delete()  # type: ignore
    try:
        db.commit()
    except Exception as e:
        print(e)
        return None
    return True


def delete_station_admin(db: Session, station_admin_user: str):
    db.query(StationAdmin).filter(StationAdmin.userId == station_admin_user).delete()  # type: ignore
    try:
        db.commit()
    except Exception as e:
        print(e)
        return None
    return True


def get_station_power_used_by_station_id(db: Session, station_id: str):
    return (
        db.query(ChargingSession)
        .filter(ChargingSession.station_id == station_id)
        .all()
    )
