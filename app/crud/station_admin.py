from sqlalchemy.orm import Session
from app.models.station_admins import StationAdmin
from app.crud import station, user
from sqlalchemy import and_


def add_admin_station(db: Session, station_id: str, admin_id: str):
    try:
        if not station.get_station_by_id(db, station_id):
            return False
        if not user.get_user_by_id(db, admin_id):
            return False
        db_station_admin = StationAdmin(stationId=station_id, user_id=admin_id)
        db.add(db_station_admin)
        db.commit()
        db.refresh(db_station_admin)
        return db_station_admin
    except Exception as e:
        print(e)
        return None


def get_admin_station_by_station_id(db: Session, station_id: str):
    try:
        return db.query(StationAdmin).filter(StationAdmin.stationId == station_id).all()  # type: ignore
    except Exception as e:
        print(e)
        return None


def update_admin_station(db: Session, station_id: str, admin_id: str):
    try:
        db.query(StationAdmin).filter(StationAdmin.stationId == station_id).update({"userId": admin_id})  # type: ignore
        db.commit()
        return db.query(StationAdmin).filter(StationAdmin.stationId == station_id).first()  # type: ignore
    except Exception as e:
        print(e)
        return None


def delete_admin_station(db: Session, station_id: str, admin_id: str):
    try:
        db.query(StationAdmin).filter(and_(StationAdmin.stationId == station_id, StationAdmin.user_id == admin_id)).delete()  # type: ignore
        db.commit()
        return True
    except Exception as e:
        print(e)
        return False
