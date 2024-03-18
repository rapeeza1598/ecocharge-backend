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


def update_user(db: Session, user_id: str, user: updateUser):
    db_user = db.query(User).filter(User.id == user_id).first()  # type: ignore
    db.query(User).filter(User.id == user_id).update(user)  # type: ignore
    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        print(e)
        return None
    return db_user


def update_user_by_super_admin(db: Session, user_id: str, user: updateUserBySuperAdmin):
    db_user = db.query(User).filter(User.id == user_id).first()  # type: ignore
    db.query(User).filter(User.id == user_id).update(user)  # type: ignore
    try:
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
            db.query(User).filter(User.id == user_id).update({User.balance: User.balance + amount})  # type: ignore
            db.commit()
            db.refresh(db_user)
        except Exception as e:
            print(e)
            return None
    return db_user


def disable_user(db: Session, user_id: str):
    db_user = db.query(User).filter(User.id == user_id).first()  # type: ignore
    if db_user is not None:
        try:
            db.query(User).filter(User.id == user_id).update({User.is_active: False})  # type: ignore
            db.commit()
            db.refresh(db_user)
        except Exception as e:
            print(e)
            return None
    return db_user


def update_user_password(db: Session, user_id: str, password: str):
    db_user = db.query(User).filter(User.id == user_id).first()  # type: ignore
    if db_user is not None:
        try:
            db.query(User).filter(User.id == user_id).update({User.hashed_password: password})  # type: ignore
            db.commit()
            db.refresh(db_user)
        except Exception as e:
            print(e)
            return None
    return db_user


def change_password_current_user(db: Session, user_id: str, password: str):
    db_user = db.query(User).filter(User.id == user_id).first()  # type: ignore
    if db_user is not None:
        try:
            if not security.verify_password(db_user.hashed_password, password):
                return None
            pass_hash = security.password_hash(password)
            db.query(User).filter(User.id == user_id).update({User.hashed_password: pass_hash})  # type: ignore
            db.commit()
            db.refresh(db_user)
        except Exception as e:
            print(e)
            return None
    return db_user
