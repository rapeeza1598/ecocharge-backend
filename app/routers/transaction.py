from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.crud.transaction import get_transactions
from app.database import get_db
from app.schemas.transaction import Transaction
from app.schemas.user import User


router = APIRouter(
    prefix="/transaction",
    tags=["Transaction"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[Transaction])
async def read_transactions(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return get_transactions(db, skip=skip, limit=limit)