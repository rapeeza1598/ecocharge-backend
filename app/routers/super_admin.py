from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.station import delete_station, get_station_admins, get_station_by_id
from app.crud.station_admin import add_admin_station, delete_admin_station
from app.crud.transaction import get_transactions
from app.crud.user import (
    create_user_by_super_admin,
    get_user_by_email,
    get_user_by_id,
    get_users,
    update_user_by_super_admin,
)
from app.database import get_db
from app.models.station_admins import StationAdmin
from app.schemas.station import createStation
from app.schemas.user import (
    User,
    changePasswordBySuperAdmin,
    createUserBySuperAdmin,
    updateUserBySuperAdmin,
)
from app.core.security import get_current_user, password_hash
from app.crud.logs import create_log_info


router = APIRouter(
    prefix="/super_admin",
    tags=["Super admin"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register/user")
async def register_user_by_super_admin(
    user: createUserBySuperAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if user.password != user.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    user.password = password_hash(user.password)
    if create_user_by_super_admin(db, user):
        user_activity = f"User {current_user.email} registered user {user.email}"
        create_log_info(db, str(current_user.id), user_activity, type_log="user")
        return {"message": "User registered successfully"}
    raise HTTPException(status_code=400, detail="User registration failed")


@router.get("/users", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 10,
    is_active: bool = None, # type: ignore
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user,
    ),
):
    if current_user.role not in ["superadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return get_users(db, skip=skip, limit=limit, is_active=is_active)


@router.put(
    "/users/{user_id}",response_model=User
)
async def update_user_by_id(
    user_id: str,
    user: updateUserBySuperAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        if update_user := update_user_by_super_admin(db, user_id, user):
            user_activity = f"User {current_user.email} updated user {user_id}"
            create_log_info(db, str(current_user.id), user_activity, type_log="user")
            return update_user
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="User not updated") from e


@router.put("/users/{user_id}/disable")
async def disable_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if current_user.role not in ["superadmin"]:
            raise HTTPException(status_code=401, detail="Unauthorized")
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.is_active = False # type: ignore
        db.commit()
        user_activity = f"User {current_user.email} disabled user {user_id}"
        create_log_info(db, str(current_user.id), user_activity, type_log="user")
        return {"message": "User disabled successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="User not disabled") from e


@router.put("/users/{user_id}/password")
async def update_user_password_by_superadmin(
    user_id: str,
    password: changePasswordBySuperAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if password.password != password.confirmPassword:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        user.hashed_password = password_hash(password.password)
        db.commit()
        user_activity = f"User {current_user.email} updated password for user {user_id}"
        create_log_info(db, str(current_user.id), message=user_activity, type_log="user")
        return {"message": "Password updated successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Password not updated") from e