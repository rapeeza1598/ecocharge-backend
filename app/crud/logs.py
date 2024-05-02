import datetime
from sqlalchemy.orm import Session
from app.models.logs import Logs
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def create_log_info(db: Session, user_id: str, message: str, type_log: str, station_id: str = None, charging_booth_id: str = None, topup_id: str = None):  # type: ignore
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    message = f"{formatted_datetime} - INFO - {message}"
    try:
        db_log = Logs(
            user_id=user_id,
            message=message,
            type_log=type_log,
            station_id=station_id,
            charging_booth_id=charging_booth_id,
            topup_id=topup_id,
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    except Exception as e:
        print(e)
        return None


def get_logs(db: Session, skip: int, limit: int):
    try:
        return db.query(Logs).offset(skip).limit(limit).all()  # type: ignore
    except Exception as e:
        print(e)
        return None


def get_logs_by_user_id(db: Session, user_id: str, skip: int = 0, limit: int = 10):
    try:
        return db.query(Logs).filter(Logs.user_id == user_id).offset(skip).limit(limit).all()  # type: ignore
    except Exception as e:
        print(e)
        return None


def get_logs_by_station_id(
    db: Session, station_id: str, skip: int = 0, limit: int = 10
):
    try:
        return db.query(Logs).filter(Logs.station_id == station_id).offset(skip).limit(limit).all()  # type: ignore
    except Exception as e:
        print(e)
        return None


def get_logs_by_charging_booth_id(
    db: Session, charging_booth_id: str, skip: int = 0, limit: int = 10
):
    try:
        return db.query(Logs).filter(Logs.charging_booth_id == charging_booth_id).offset(skip).limit(limit).all()  # type: ignore
    except Exception as e:
        print(e)
        return None


def delete_log_by_time(db: Session, start_time: str, end_time: str):
    try:
        db.query(Logs).filter(Logs.created_at >= start_time).filter(Logs.created_at <= end_time).delete()  # type: ignore
        db.commit()
        return True
    except Exception as e:
        print(e)
        return False
