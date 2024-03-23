from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.crud.transaction import create_transaction
from app.crud.user import get_user_by_id, update_user_balance
from app.database import get_db
from app.schemas.user import User
from decimal import Decimal
from enum import Enum


class TopupType(str, Enum):
    cash = "cash"
    mastercard = "mastercard"
    visa = "visa"
    paypal = "paypal"


router = APIRouter(
    prefix="/top_up",
    tags=["Top up"],
    responses={404: {"description": "Not found"}},
)


@router.put("/{user_id}")
async def topup_user_balance(
    user_id: str,
    amount: float = 0.0,
    select_topup: TopupType = TopupType.cash,
    description: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount should be greater than 0")
    if current_user.role not in ["superadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    amount_decimal = Decimal(amount)
    if not create_transaction(
        db, user_id, float(amount_decimal), select_topup, description
    ) or not update_user_balance(db, user_id, amount):
        raise HTTPException(status_code=400, detail="Transaction not created")
    return {"message": "User balance updated successfully"}
