import os
import secrets
from fastapi import APIRouter, BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pyotp import TOTP
from sqlalchemy.orm import Session
from app.core import security
from app.crud.token import create_token, get_token, update_token_by_email
from app.crud.user import create_user, get_user_by_email
from app.database import Base, engine, get_db
from app.models import (
    charging_booths,
    charging_sessions,
    station_admins,
    stations,
    transactions,
    users,
    topups,
    tokens,
    user_avatars,
    logs,
)
from app.schemas.token import setNewPassword
from app.schemas.user import EmailRequest, EmailRequest, createUser
from app.routers import (
    user,
    super_admin,
    station,
    transaction,
    charging_session,
    charging_booth,
    station_admin,
    topup,
    image,
    log,
)
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, select_autoescape

models = [
    users.User,
    stations.Station,
    transactions.Transaction,
    charging_sessions.ChargingSession,
    charging_booths.ChargingBooth,
    station_admins.StationAdmin,
    topups.Topups,
    tokens.Token,
    user_avatars.UserAvatar,
    logs.Logs,
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
    "https://ev-dashboard-ten.vercel.app",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")


def generate_token() -> str:
    return secrets.token_urlsafe(16)

def generate_otp(email: str) -> str:
    totp = TOTP(str(os.getenv("OTP_SECRET")))
    return totp.now()

def verify_otp(email: str, otp: str) -> bool:
    totp = TOTP(str(os.getenv("OTP_SECRET")))
    return totp.verify(otp)

def send_email(email: str, subject: str, html_content: str):
    smtp_user = str(os.getenv("SMTP_USER"))
    smtp_password = str(os.getenv("APP_PASSWORD"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)

        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = email
        msg["Subject"] = subject

        msg.attach(MIMEText(html_content, "html"))

        server.send_message(msg)

def send_reset_email(email: str, token: str):
    template_env = Environment(
        loader=FileSystemLoader("static/"),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = template_env.get_template("reset_email.html")
    html_content = template.render(token=token)

    send_email(email, "Password Reset Request", html_content)
    print(f"Sending reset email to {email} with token {token}")

def send_otp_email(email: str, otp: str):
    template_env = Environment(
        loader=FileSystemLoader("static/"),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = template_env.get_template("otp.html")
    html_content = template.render(otp=otp)

    send_email(email, "Verification Code", html_content)
    print(f"Sending OTP email to {email} with code {otp}")


@app.get("/")
def read_root():
    # return {"msg": "Hello World"}
    return FileResponse("./static/index.html")


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


@app.post("/reset_password/")
async def reset_password(email: EmailRequest, background_tasks: BackgroundTasks,db: Session = Depends(get_db)):
    token = generate_token()
    print(f"Generated token: {token}")
    if update_token_by_email(db, token, email.email):
        print("Token updated")
        background_tasks.add_task(send_reset_email, email.email, token)
    elif get_user_by_email(db, email.email):
        create_token(db, token, email.email)
        print("Token created")
        background_tasks.add_task(send_reset_email, email.email, token)
    return {"message": "Password reset email sent"}

@app.get("/reset_password/{token}")
async def validate_token(token: str, db: Session = Depends(get_db)):
    # return {"message": "Token is valid"}
    if get_token(db, token):
        return FileResponse("./static/change_password.html")
    else:
        return FileResponse("./static/404.html")

@app.post("/set_password/")
async def set_new_password(setNewPassword: setNewPassword, db: Session = Depends(get_db)):
    token = setNewPassword.token
    new_password = setNewPassword.new_password
    if not new_password:
        raise HTTPException(status_code=400, detail="Password cannot be empty")
    db_token = get_token(db, token)
    if not db_token:
        raise HTTPException(status_code=400, detail="Invalid token")
    email = db_token.email
    user = get_user_by_email(db, str(email))
    user.hashed_password = security.password_hash(new_password) # type: ignore
    db.delete(db_token)
    db.commit()
    return {"message": "Password reset successfully"}

@app.post("/send-otp/")
async def send_otp(email_request: EmailRequest, background_tasks: BackgroundTasks):
    # Generate OTP
    otp = generate_otp(email_request.email)

    # Send OTP via email
    background_tasks.add_task(send_otp_email, email_request.email, otp)
    return {"message": "OTP sent successfully"}

@app.post("/verify-otp/")
async def verify_my_otp(email_request: EmailRequest, otp: str):
    if is_valid := verify_otp(email_request.email, otp=otp):
        return {"detail": "OTP is valid"}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP")



app.include_router(user.router)
app.include_router(super_admin.router)
app.include_router(station.router)
app.include_router(station_admin.router)
app.include_router(charging_booth.router)
app.include_router(transaction.router)
app.include_router(charging_session.router)
app.include_router(topup.router)
app.include_router(image.router)
app.include_router(log.router)
