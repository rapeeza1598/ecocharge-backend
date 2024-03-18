from sqlalchemy.orm import Session
from app.models.station_admins import StationAdmin
from sqlalchemy import and_
def add_admin_station(db: Session, station_id: str, admin_id: str):
    try:
        admin_in_station = get_admin_station_by_station_id(db, station_id)
        if admin_in_station is not None:  # Check if admin_in_station is not None
            for admin in admin_in_station:
                if str(admin.userId) == admin_id:  # Cast admin.userId to string before comparing
                    return None
        new_admin_station = StationAdmin(stationId=station_id, userId=admin_id)
        db.add(new_admin_station)
        db.commit()
        db.refresh(new_admin_station)
        return new_admin_station
    except Exception as e:
        print(e)
        return None


def get_admin_station_by_station_id(db: Session, station_id: str):
    try:
        return db.query(StationAdmin).filter(StationAdmin.stationId == station_id).all() # type: ignore
    except Exception as e:
        print(e)
        return None

def update_admin_station(db: Session, station_id: str, admin_id: str):
    try:
        db.query(StationAdmin).filter(StationAdmin.stationId == station_id).update({"userId": admin_id}) # type: ignore
        db.commit()
        return db.query(StationAdmin).filter(StationAdmin.stationId == station_id).first() # type: ignore
    except Exception as e:
        print(e)
        return None

def delete_admin_station(db: Session, station_id: str, admin_id: str):
    try:
        db.query(StationAdmin).filter(and_(StationAdmin.stationId == station_id, StationAdmin.user_id == admin_id)).delete() # type: ignore
        db.commit()
        return True
    except Exception as e:
        print(e)
        return False