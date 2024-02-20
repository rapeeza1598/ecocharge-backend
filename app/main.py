import uuid
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app import crud, models, schemas,security
from app.database import SessionLocal, engine
from decimal import Decimal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "https://example.com",
    "https://staging.example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

# view database url
@app.get("/db")
def read_db():
    return {"db_url": engine.url[5]}

@app.post("/token")
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if user and security.verify_password(form_data.password, user.hashed_password):
        token = security.create_access_token(data={"sub": user.email})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect email or password")

@app.post("/register")
async def register_user(user: schemas.createUser, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if user.password!=user.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    user.password = security.password_hash(user.password)
    crud.create_user(db, user)
    return {"message": "User registered successfully"}

@app.post("/register/by_superadmin")
async def register_user_by_superadmin(user: schemas.createUserBySuperAdmin, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if user.password!=user.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    user.password = security.password_hash(user.password)
    crud.create_user_by_super_admin(db, user)
    return {"message": "User registered successfully"}

# Get All Users from DB response_model list of User and check access token
@app.get("/users", response_model=list[schemas.User])
async def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

# update user by current user
@app.put("/users", response_model=schemas.User)
async def update_user(user: schemas.updateUser, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    db_user = crud.update_user(db, current_user.id, user)
    return db_user

@app.put("/users/{user_id}", response_model=schemas.User)
async def update_user_by_id(user_id: str, user: schemas.updateUserBySuperAdmin, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    db_user = crud.update_user_by_super_admin(db, user_id, user)
    return db_user

# user balance topup
@app.put("/users/{user_id}/topup")
async def topup_user_balance(user_id: str, amount: float, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    amount_decimal = Decimal(amount)
    user.balance += amount_decimal
    db.commit()
    return {"message": "User balance updated successfully"}

# delete user by id disabled
@app.put("/users/{user_id}/disable")
async def disable_user(user_id: str, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"message": "User disabled successfully"}

@app.post("/stations", response_model=schemas.Station)
async def create_station(station: schemas.createStation, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    db_station = crud.create_station(db, station)
    if not db_station:
        raise HTTPException(status_code=400, detail="Station not created")
    return db_station

@app.get("/stations", response_model=list[schemas.Station])
async def read_stations(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    stations = crud.get_stations(db, skip=skip, limit=limit)
    return stations

@app.get("/stations/{station_id}", response_model=schemas.Station)
async def read_station_by_id(station_id: str, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    station = crud.get_station_by_id(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station

@app.put("/stations/{station_id}", response_model=schemas.Station)
async def update_station(station_id: str, station: schemas.updateStation, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    db_station = crud.update_station(db, station_id, station)
    return db_station

# set admin for station
@app.put("/stations/{station_id}/admins/{user_id}")
async def create_station_admin(station_id: str, user_id: str, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    station = crud.get_station_by_id(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    station_admin = schemas.createStationAdmin(userId=user_id,stationId=station_id)
    db_station_admin = crud.create_station_admin(db, station_admin)
    return {"message": "Station Admin created successfully"}

# start charging session
@app.post("/charging_sessions")
async def start_charging_session(charging_session: schemas.ChargingSession, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    station = crud.get_station_by_id(db, charging_session.stationId)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    user = crud.get_user_by_id(db, charging_session.userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.balance<0: # type: ignore
        raise HTTPException(status_code=400, detail="Insufficient balance")
    db_charging_session = crud.create_charging_session(db, charging_session)
    return db_charging_session

# update charging session by station id
@app.put("/charging_sessions/{charging_session_id}/stations/{station_id}")
async def update_charging_session_by_station_id(charging_session_id: str, station_id: str, charging_session: schemas.updateChargingSession, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    db_charging_session = crud.update_charging_session_by_station_id(db, charging_session_id, station_id, charging_session)
    return db_charging_session

# stop charging session
@app.put("/charging_sessions/{charging_session_id}")
async def stop_charging_session(charging_session_id: str, charging_session: schemas.updateChargingSession, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    db_charging_session = crud.stop_charging_session(db, charging_session_id, charging_session)
    return db_charging_session

# get and sum all power used by station id
@app.get("/stations/{station_id}/power_used")
async def get_station_power_used(station_id: str, db: Session = Depends(get_db),current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin" or current_user.role != "stationadmin":
        raise HTTPException(status_code=401, detail="Not permitted to access this resource")
    charging_sessions = crud.get_charging_session_by_station_id(db, station_id)
    power_used = 0
    for session in charging_sessions:
        power_used += session.powerUsed
    return{"stationId":station_id,"powerUsed":power_used}

