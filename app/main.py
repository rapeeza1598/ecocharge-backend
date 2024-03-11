from fastapi import FastAPI, Depends, HTTPException, WebSocket
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app import crud, models, schemas,security
from app.database import engine
from decimal import Decimal
from uuid import UUID

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://example.com",
    "https://staging.example.com",
    "ev-dashboard-ten.vercel.app",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello World"}

# view database url
@app.get("/db")
def read_db():
    return {"db_url": engine.url[5]}

@app.post("/token",tags=["user"])
async def login_for_access_token(db: Session = Depends(crud.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if user and security.verify_password(form_data.password, user.hashed_password):
        token = security.create_access_token(data={"sub": user.email})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect email or password")

@app.post("/register",tags=["user"])
async def register_user(user: schemas.createUser, db: Session = Depends(crud.get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if user.password!=user.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    user.password = security.password_hash(user.password)
    crud.create_user(db, user)
    return {"message": "User registered successfully"}

@app.post("/register/by_superadmin",tags=["superadmin"])
async def register_user_by_superadmin(user: schemas.createUserBySuperAdmin, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if user.password!=user.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    user.password = security.password_hash(user.password)
    crud.create_user_by_super_admin(db, user)
    return {"message": "User registered successfully"}

# get user me
@app.get("/users/me", response_model=schemas.User ,tags=["user"])
async def read_users_me(db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    return current_user

# Get All Users from DB response_model list of User and check access token
@app.get("/users", response_model=list[schemas.User],tags=["superadmin"])
async def read_users(skip: int = 0, limit: int = 10,is_active: bool = None, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user,)): # type: ignore
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return crud.get_users(db, skip=skip, limit=limit, is_active=is_active)

# update user by current user
@app.put("/users", response_model=schemas.updateUser, tags=["user"])
async def update_user(user: schemas.updateUser, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    return crud.update_user(db, str(current_user.id), user)

@app.put("/users/{user_id}", response_model=schemas.updateUserBySuperAdmin, tags=["superadmin"])
async def update_user_by_id(user_id: str, user: schemas.updateUserBySuperAdmin, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return crud.update_user_by_super_admin(db, user_id, user)

# user balance topup
@app.put("/users/{user_id}/topup",tags=["superadmin"])
async def topup_user_balance(user_id: str, amount: float, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    amount_decimal = Decimal(amount)
    # save transaction
    transaction = schemas.createTransaction(userId=UUID(user_id), amount=float(amount_decimal), transactionType="topup", description="User balance topup")
    db_transaction = crud.create_transaction(db, transaction)
    if not db_transaction:
        raise HTTPException(status_code=400, detail="Transaction not created")
    user.balance += amount_decimal
    db.commit()
    return {"message": "User balance updated successfully"}

# delete user by id disabled
@app.put("/users/{user_id}/disable",tags=["superadmin"])
async def disable_user(user_id: str, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"message": "User disabled successfully"}

# update user password
@app.post("/users/password",tags=["user"])
async def update_user_password(password: schemas.updatePassword, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    user = crud.get_user_by_email(db,current_user.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # check old password
    if not security.verify_password(password.oldPassword, user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    hash_pass = security.password_hash(password.password)
    if password.password != password.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    user.hashed_password = hash_pass
    db.commit()
    return {"message": "Password updated successfully"} 

# update user password by superadmin
@app.put("/users/{user_id}/password",tags=["superadmin"])
async def update_user_password_by_superadmin(user_id: str, password: schemas.updatePasswordBySuperAdmin, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if password.password!=password.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    user.hashed_password = security.password_hash(password.password)
    db.commit()
    return {"message": "Password updated successfully"}

@app.post("/stations", response_model=schemas.Station, tags=["superadmin"])
async def create_station(station: schemas.createStation, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    if db_station := crud.create_station(db, station):
        return db_station
    else:
        raise HTTPException(status_code=400, detail="Station not created")

@app.get("/stations", response_model=list[schemas.Station], tags=["station"])
async def read_stations(skip: int = 0, limit: int = 10, db: Session = Depends(crud.get_db)):
    return crud.get_stations(db, skip=skip, limit=limit)

@app.get("/stations/{station_id}", response_model=schemas.Station, tags=["station"])
async def read_station_by_id(station_id: str, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if station := crud.get_station_by_id(db, station_id):
        return station
    else:
        raise HTTPException(status_code=404, detail="Station not found")

@app.put("/stations/{station_id}", response_model=schemas.Station,tags=["superadmin"])
async def update_station(station_id: str, station: schemas.updateStation, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return crud.update_station(db, station_id, station)

# set admin for station
@app.put("/stations/{station_id}/admins/{user_id}",tags=["superadmin"])
async def create_station_admin(station_id: str, user_id: str, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
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

# delete station by superadmin
@app.delete("/stations/{station_id}",tags=["superadmin"])
async def delete_station_by_superadmin(station_id: str, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    try:
        if current_user.role != "superadmin":
            raise HTTPException(status_code=401, detail="Unauthorized")
        station = crud.get_station_by_id(db, station_id)
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")
        crud.delete_station(db, station_id)
        return {"message": "Station deleted successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Station not deleted")

# delete station admin by superadmin
@app.delete("/stations/{station_id}/admins/{user_id}",tags=["superadmin"])
async def delete_station_admin_by_superadmin(station_id: str, user_id: str, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    station_admin = crud.get_station_admin_by_id(db, user_id)
    if not station_admin:
        raise HTTPException(status_code=404, detail="Station Admin not found")
    crud.delete_station_admin(db, user_id)
    return {"message": "Station Admin deleted successfully"}

# start charging session
@app.post("/charging_sessions",tags=["charging"])
async def create_charging_session(charging_session: schemas.createChargingSession, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    user = crud.get_user_by_id(db, charging_session.userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    station = crud.get_station_by_id(db, charging_session.stationId)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    if user.balance < 0:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    if db_charging_session := crud.create_charging_session(
        db, charging_session
    ):
        return db_charging_session
    else:
        raise HTTPException(status_code=400, detail="Charging session not created")

# update charging session by station id
@app.put("/charging_sessions/{charging_session_id}/stations/{station_id}",tags=["superadmin"])
async def update_charging_session_by_station_id(charging_session_id: str, station_id: str, charging_session: schemas.updateChargingSession, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return crud.update_charging_session_by_station_id(
        db, charging_session_id, station_id, charging_session
    )

# stop charging session
@app.put("/charging_sessions/{charging_session_id}",tags=["charging"])
async def stop_charging_session(charging_session_id: str, charging_session: schemas.updateChargingSession, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    return crud.stop_charging_session(db, charging_session_id, charging_session)

# get and sum all power used by station id
@app.get("/stations/{station_id}/power_used",tags=["station"])
async def get_station_power_used(station_id: str, db: Session = Depends(crud.get_db),current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role == "user":
        raise HTTPException(status_code=401, detail="Not permitted to access this resource")
    charging_sessions = crud.get_charging_session_by_station_id(db, station_id)
    power_used = sum(session.powerUsed for session in charging_sessions)
    return{"stationId":station_id,"powerUsed":power_used}

# get all transactions
@app.get("/transactions", response_model=list[schemas.Transaction],tags=["superadmin"])
async def read_transactions(skip: int = 0, limit: int = 10, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return crud.get_transactions(db, skip=skip, limit=limit)

# get station admins
@app.get("/stations/{station_id}/admins", response_model=list[schemas.User],tags=["superadmin"])
async def read_station_admins(station_id: str, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role == "user":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return crud.get_station_admins(db, station_id)

@app.get("/stations/{station_id}/details", tags=["station"])
async def read_station_details(station_id: str, db: Session = Depends(crud.get_db), current_user: schemas.User = Depends(security.get_current_user)):
    if current_user.role == "user":
        raise HTTPException(status_code=401, detail="Not permitted to access this resource")
    station = crud.get_station_by_id(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    charging_sessions = crud.get_charging_session_by_station_id(db, station_id)
    power_used = sum(session.powerUsed for session in charging_sessions)
    return {"station": station, "powerUsed": power_used}

@app.websocket("/ws{charging_session_id}")
async def websocket_endpoint(websocket: WebSocket, charging_session_id: str):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
    await websocket.close()