from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core import security 
from app.crud.user import create_user, get_user_by_email
from app.database import Base, engine, get_db
from app.models import (
    charging_booths,
    charging_sessions,
    station_admins,
    stations,
    transactions,
    users,
)
from app.schemas.user import createUser
from app.routers import (
    user,
    super_admin,
    station,
    transaction,
    charging_session,
    charging_booth,
    station_admin,
)


models = [
    users.User,
    stations.Station,
    transactions.Transaction,
    charging_sessions.ChargingSession,
    charging_booths.ChargingBooth,
    station_admins.StationAdmin,
]
Base.metadata.create_all(bind=engine, tables=[model.__table__ for model in models])


app = FastAPI()
api_router = APIRouter()

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
    return {"msg": "Hello World"}


@app.get("/db")
def read_db():
    return {"db_url": engine.url[5]}


@app.post("/token")
async def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if user and security.verify_password(form_data.password, user.hashed_password):
        token = security.create_access_token(data={"sub": user.email})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect email or password")


@app.post("/register")
async def register_user(user: createUser, db: Session = Depends(get_db)):
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if user.password != user.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    user.password = security.password_hash(user.password)
    create_user(db, user)
    return {"message": "User registered successfully"}


app.include_router(user.router)
app.include_router(super_admin.router)
app.include_router(station.router)
app.include_router(station_admin.router)
app.include_router(charging_booth.router)
app.include_router(transaction.router)
app.include_router(charging_session.router)
