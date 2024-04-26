import base64
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.crud.topup import approve_topup, get_topup_by_id, get_topups
from app.crud.transaction import create_transaction
from app.crud.user import get_user_by_id, update_user_balance
from app.database import get_db
from app.schemas.topup import TopupImage, TopupResponse
from app.schemas.user import User
from decimal import Decimal
from enum import Enum
from io import BytesIO


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


@router.get("/")
async def read_topups(
    skip: int = 0,
    limit: int = 10,
    status_approved: bool = None, # type: ignore
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if topups := get_topups(
        db, skip=skip, limit=limit, status_approved=status_approved
    ):
        return topups
    else:
        raise HTTPException(status_code=404, detail="Topups not found")


@router.put("/{user_id}")
async def topup_user_balance_by_superadmin(
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


@router.put("/{user_id}/approve/{topup_id}")
async def approve_topup_by_sueradmin(
    user_id: str,
    topup_id: str,
    is_approved: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if is_approved and not approve_topup(db, topup_id):
        raise HTTPException(status_code=400, detail="Transaction not approved")
    return {"message": "Transaction approved successfully"}


@router.get("/get_image/{topup_id}")
async def get_topup_image_by_id(
    topup_id:str,
    db: Session = Depends(get_db),
):
    if topup := get_topup_by_id(db, topup_id):
        decoded_image = (topup.image_base64).split(",", 1)
        image = BytesIO(base64.b64decode(decoded_image[1]))
        image_bytes = image.getvalue()
        return Response(content=image_bytes, media_type="image/png")
    else:
        raise HTTPException(status_code=404, detail="Topup not found")
