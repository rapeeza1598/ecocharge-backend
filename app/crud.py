import uuid
from sqlalchemy.orm import Session
from app import models, schemas
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_user(db: Session, user: schemas.createUser):
    db_user = models.User(
        firstName=user.firstName,
        lastName=user.lastName,
        email=user.email,
        phoneNumber=user.phoneNumber,
        hashed_password=user.password,
        role="user"
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        print(e)
        return None
    return db_user

def create_user_by_super_admin(db: Session, user: schemas.createUserBySuperAdmin):
    db_user = models.User(
        firstName=user.firstName,
        lastName=user.lastName,
        email=user.email,
        phoneNumber=user.phoneNumber,
        hashed_password=user.password,
        role=user.role
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        print(e)
        return None
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 10,is_active:bool = None): # type: ignore
    # if get all users is_active = None
    if is_active is None:
        return db.query(models.User).offset(skip).limit(limit).all()
    else:
        return db.query(models.User).filter(models.User.is_active == is_active).offset(skip).limit(limit).all()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()

def update_user(db: Session, user_id: str, user: schemas.updateUser):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    for var, value in user.dict().items():
        setattr(db_user, var, value) if value else None
    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        print(e)
        return None
    return db_user

def update_user_by_super_admin(db: Session, user_id: str, user: schemas.updateUserBySuperAdmin):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    for var, value in user.dict().items():
        setattr(db_user, var, value) if value else None
    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        print(e)
        return None
    return db_user

def create_station(db: Session, station: schemas.createStation):
    db_station = models.Station(
        name=station.name,
        location=station.location
    )
    try:
        db.add(db_station)
        db.commit()
        db.refresh(db_station)
    except Exception as e:
        print(e)
        return None
    return db_station

def get_stations(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Station).offset(skip).limit(limit).all()

def get_station_by_id(db: Session, station_id: str):
    return db.query(models.Station).filter(models.Station.id == station_id).first()

def update_station(db: Session, station_id: str, station: schemas.updateStation):
    db_station = db.query(models.Station).filter(models.Station.id == station_id).first()
    for var, value in station.dict().items():
        setattr(db_station, var, value) if value else None
    db.commit()
    db.refresh(db_station)
    return db_station

def create_station_admin(db: Session, station_admin: schemas.createStationAdmin):
    db_station_admin = models.StationAdmin(**station_admin.dict())
    try:
        db.add(db_station_admin)
        db.commit()
        db.refresh(db_station_admin)
    except Exception as e:
        print(e)
        return None
    return db_station_admin

def get_station_admins(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.StationAdmin).offset(skip).limit(limit).all()

def get_station_admin_by_id(db: Session, station_admin_id: str):
    return db.query(models.StationAdmin).filter(models.StationAdmin.id == station_admin_id).first()

def create_transaction(db: Session, transaction: schemas.Transaction):
    db_transaction = models.Transaction(**transaction.dict())
    try:
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
    except Exception as e:
        print(e)
        return None
    return db_transaction

def get_transactions(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Transaction).offset(skip).limit(limit).all()

def get_transaction_by_user_id(db: Session, user_id: str):
    return db.query(models.Transaction).filter(models.Transaction.userId == user_id).all()

def get_transaction_by_id(db: Session, transaction_id: str):
    return db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

def get_transaction_by_station_id(db: Session, station_id: str):
    return db.query(models.Transaction).filter(models.Transaction.stationId == station_id).all()

def create_charging_session(db: Session, charging_session: schemas.ChargingSession):
    db_charging_session = models.ChargingSession(**charging_session.dict())
    try:
        db.add(db_charging_session)
        db.commit()
        db.refresh(db_charging_session)
    except Exception as e:
        print(e)
        return None
    return db_charging_session

def get_charging_sessions(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.ChargingSession).offset(skip).limit(limit).all()

def get_charging_session_by_user_id(db: Session, user_id: str):
    return db.query(models.ChargingSession).filter(models.ChargingSession.userId == user_id).all()

def get_charging_session_by_id(db: Session, charging_session_id: str):
    return db.query(models.ChargingSession).filter(models.ChargingSession.id == charging_session_id).first()

def get_charging_session_by_station_id(db: Session, station_id: str):
    return db.query(models.ChargingSession).filter(models.ChargingSession.stationId == station_id).all()

def update_charging_session(db: Session, charging_session_id: str, charging_session: schemas.updateChargingSession):
    db_charging_session = db.query(models.ChargingSession).filter(models.ChargingSession.id == charging_session_id).first()
    for var, value in charging_session.dict().items():
        setattr(db_charging_session, var, value) if value else None
    try:
        db.commit()
        db.refresh(db_charging_session)
    except Exception as e:
        print(e)
        return None
    return db_charging_session

def update_charging_session_by_station_id(db: Session, charging_session_id: str, charging_session: schemas.updateChargingSession):
    db_charging_session = db.query(models.ChargingSession).filter(models.ChargingSession.id == charging_session_id).first()
    for var, value in charging_session.dict().items():
        setattr(db_charging_session, var, value) if value else None
    try:
        db.commit()
        db.refresh(db_charging_session)
    except Exception as e:
        print(e)
        return None
    return db_charging_session

def stop_charging_session(db: Session, charging_session_id: str, charging_session: schemas.updateChargingSession):
    db_charging_session = db.query(models.ChargingSession).filter(models.ChargingSession.id == charging_session_id).first()
    # status = "completed" if charging_session.status == "completed" else "stopped"
    setattr(db_charging_session, "status", "completed")
    setattr(db_charging_session, "endTime", charging_session.endTime)
    try:
        db.commit()
        db.refresh(db_charging_session)
    except Exception as e:
        print(e)
        return None
    return db_charging_session

def update_user_balance(db: Session, user_id: str, amount: float):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_user.balance += amount
    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        print(e)
        return None
    return db_user

def get_station_power_used_by_station_id(db: Session, station_id: str):
    return db.query(models.ChargingSession).filter(models.ChargingSession.stationId == station_id).all()

