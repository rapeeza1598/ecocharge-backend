from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.users import User
from app.schemas.user import (
    createUser,
    createUserBySuperAdmin,
    updateUser,
    updateUserBySuperAdmin,
)
from app.core import security


def create_user(db: Session, user: createUser):
    db_user = User(
        firstName=user.firstName,
        lastName=user.lastName,
        email=user.email,
        phoneNumber=user.phoneNumber,
        hashed_password=user.password,
        role="user",
    )
    if db_user is None:
        return None
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        print(e)
        return None
    return db_user


def create_user_by_super_admin(db: Session, user: createUserBySuperAdmin):
    db_user = User(
        firstName=user.firstName,
        lastName=user.lastName,
        email=user.email,
        phoneNumber=user.phoneNumber,
        hashed_password=user.password,
        role=user.role,
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        print(e)
        return None
    return db_user


def get_users(db: Session, skip: int = 0, limit: int = 10, is_active: bool = None):  # type: ignore
    if is_active is None:
        return db.query(User).offset(skip).limit(limit).all()
    else:
        return (
            db.query(User)
            .filter(User.is_active == is_active)
            .offset(skip)
            .limit(limit)
            .all()
        )


def get_user_by_email(db: Session, email: str, is_active: bool = None):  # type: ignore
    if is_active is None:
        return db.query(User).filter(User.email == email).first()  # type: ignore
    else:
        return db.query(User).filter(User.email == email, User.is_active == is_active).first()  # type: ignore


def get_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()  # type: ignore

def get_user_by_email_verify(db: Session, email: str): 
    return db.query(User).filter(User.email == email, User.is_verify == False).first()  # type: ignore


def update_user(db: Session, user_id: str, user: updateUser):
    db_user = db.query(User).filter(User.id == user_id).first()  # type: ignore
    setattr(db_user, "firstName", user.firstName)
    setattr(db_user, "lastName", user.lastName)
    setattr(db_user, "phoneNumber", user.phoneNumber)
    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        print(e)
        return None
    return db_user


def update_user_by_super_admin(db: Session, user_id: str, user: updateUserBySuperAdmin):
    db_user = db.query(User).filter(User.id == user_id).first()  # type: ignore
    list_data = ["firstName", "lastName", "phoneNumber","email", "role", "is_active"]
    try:
        for data in list_data:
            if hasattr(user, data):
                setattr(db_user, data, getattr(user, data))
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        print(e)
        return None
    return db_user


def update_user_balance(db: Session, user_id: str, amount: float):
    db_user = db.query(User).filter(User.id == user_id).first()  # type: ignore
    if db_user is not None:
        try:
            updated_balance = db_user.balance + Decimal(amount)
            setattr(db_user, "balance", updated_balance)
            db.commit()
            db.refresh(db_user)
            return db_user
        except Exception as e:
            print(e)
            return None


def disable_user(db: Session, user_id: str):
    db_user = db.query(User).filter(User.id == user_id).first()  # type: ignore
    if db_user is not None:
        try:
            setattr(db_user, "is_active", False)
            db.commit()
            db.refresh(db_user)
        except Exception as e:
            print(e)
            return None


def update_user_password(db: Session, user_id: str, password: str):
    db_user = db.query(User).filter(User.id == user_id).first()  # type: ignore
    if db_user is not None:
        try:
            setattr(db_user, "hashed_password", security.password_hash(password))
            db.commit()
            db.refresh(db_user)
            return db_user
        except Exception as e:
            print(e)
            return None


def check_password_current_user(db: Session, user_id: str, password: str):
    db_user = db.query(User).filter(User.id == user_id).first()  # type: ignore
    if db_user is not None:
        try:
            if not security.verify_password(password, db_user.hashed_password):
                return None
            return True
        except Exception as e:
            print(e)
            return None

def verify_user_by_otp(db: Session, email: str):
    db_user = db.query(User).filter(User.email == email).first()  # type: ignore
    if db_user is not None:
        try:
            userIsVerify = bool(db_user.is_verify)
            if userIsVerify:
                return None
            setattr(db_user, "is_active", True)
            setattr(db_user, "is_verify", True)
            db.commit()
            db.refresh(db_user)
        except Exception as e:
            print(e)
            return None
    return db_user