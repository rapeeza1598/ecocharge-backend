from sqlalchemy.orm import Session
from app.models.charging_booths import ChargingBooth


def add_charging_booth(db: Session, booth_name: str, station_id: str):
    try:
        new_booth = ChargingBooth(booth_name=booth_name, station_id=station_id)
        db.add(new_booth)
        db.commit()
        db.refresh(new_booth)
        return new_booth
    except Exception as e:
        print(e)
        return None


def get_all_charging_booths(db: Session, skip: int = 0, limit: int = 10):
    return db.query(ChargingBooth).offset(skip).limit(limit).all()


def get_charging_booths_by_station_id(
    db: Session, station_id: str, skip: int = 0, limit: int = 10
):
    return db.query(ChargingBooth).filter(ChargingBooth.station_id == station_id).offset(skip).limit(limit).all()  # type: ignore


def get_charging_booth_by_id(db: Session, booth_id: str):
    return db.query(ChargingBooth).filter(ChargingBooth.booth_id == booth_id).first()  # type: ignore


def get_charging_booth_by_station_id(db: Session, station_id: str):
    return db.query(ChargingBooth).filter(ChargingBooth.station_id == station_id).all()  # type: ignore


def update_charging_booth_status(db: Session, booth_id: str, status: str):
    db.query(ChargingBooth).filter(ChargingBooth.booth_id == booth_id).update({"status": status})  # type: ignore
    db.commit()
    return db.query(ChargingBooth).filter(ChargingBooth.booth_id == booth_id).first()  # type: ignore


def update_charging_booth_rate(db: Session, booth_id: str, charging_rate: float):
    db.query(ChargingBooth).filter(ChargingBooth.booth_id == booth_id).update({"charging_rate": charging_rate})  # type: ignore
    db.commit()
    return db.query(ChargingBooth).filter(ChargingBooth.booth_id == booth_id).first()  # type: ignore


def update_charging_booth(db: Session, booth_id: str, booth_name: str, station_id: str):
    db.query(ChargingBooth).filter(ChargingBooth.booth_id == booth_id).update({"booth_name": booth_name, "station_id": station_id})  # type: ignore
    db.commit()
    return db.query(ChargingBooth).filter(ChargingBooth.booth_id == booth_id).first()  # type: ignore


def delete_charging_booth(db: Session, booth_id: str):
    db.query(ChargingBooth).filter(ChargingBooth.booth_id == booth_id).delete()  # type: ignore
    db.commit()
    return True
