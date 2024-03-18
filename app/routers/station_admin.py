from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.crud.station_admin import add_admin_station, delete_admin_station
from app.database import get_db
from app.schemas.user import User


router = APIRouter(
    prefix="/station_admin",
    tags=["Station Admin"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def read_station_admins():
    return {"message": "Read station admins"}

@router.post("/{station_id}/admins/{user_id}")
async def create_station_admin(
    station_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if add_admin_station(db, station_id, user_id):
        return {"message": "Station Admin added successfully"}
    else:
        raise HTTPException(status_code=400, detail="Station Admin not added")
    
@router.delete("/{station_id}/admins/{user_id}")
async def delete_station_admin_by_superadmin(
    station_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if delete_admin_station(db, station_id, user_id):
        return {"message": "Station Admin deleted successfully"}
    else:
        raise HTTPException(status_code=400, detail="Station Admin not deleted")