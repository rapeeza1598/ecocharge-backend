import base64
from decimal import Decimal
import os
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.crud.topup import approve_topup, create_topup, get_topup_by_id, get_topups
from app.crud.transaction import create_transaction
from app.crud.user import get_user_by_id, update_user_balance
from app.database import get_db
from app.schemas.topup import TopupCreate, TopupImage, TopupResponse
from app.schemas.user import User
from decimal import Decimal
from enum import Enum
from io import BytesIO
import httpx
from app.crud.logs import create_log_info


class TopupType(str, Enum):
    cash = "cash"
    mastercard = "mastercard"
    visa = "visa"
    paypal = "paypal"
    promptpay = "promptpay"


router = APIRouter(
    prefix="/top_up",
    tags=["Top up"],
    responses={404: {"description": "Not found"}},
)


async def verify_image(image_base64):
    url = "https://developer.easyslip.com/api/v1/verify"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('EasySlip_API_KEY')}",
    }
    data = {"image": image_base64}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        return response.status_code == 200


@router.get("/")
async def read_topups(
    skip: int = 0,
    limit: int = 10,
    status_approved: bool = None,  # type: ignore
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if topups := get_topups(
        db, skip=skip, limit=limit, status_approved=status_approved
    ):
        return topups
    else:
        raise HTTPException(status_code=404, detail="Topups not found")


@router.post("/")
async def topup_user(
    topup_data: TopupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if topup_data.amount < 0:
            raise HTTPException(
                status_code=400, detail="Amount should be greater than 0"
            )
        # check size of image limit to 4MB
        if len(topup_data.image_base64) > 4 * 1024 * 1024:
            raise HTTPException(
                status_code=400, detail="Image size should be less than 4MB"
            )
        base64.b64decode(topup_data.image_base64)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Invalid image base64") from e
    if topup := create_topup(db, str(current_user.id), topup_data):
        # if await verify_image(topup_data.image_base64):
        #     approve_topup(db, str(topup.id))
        #     update_user_balance(db, str(current_user.id), topup_data.amount)
        return {"message": "topup successfully waiting for approval"}
    else:
        raise HTTPException(status_code=400, detail="topup not created")


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
    if current_user.role not in ["superadmin", "stationadmin"]:
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
    if current_user.role not in ["superadmin", "stationadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    my_topup = get_topup_by_id(db, topup_id)
    if my_topup.status_approved:  # type: ignore
        raise HTTPException(status_code=400, detail="Topup already approved")
    my_approve_topup = approve_topup(db, topup_id)
    if is_approved and not my_approve_topup:
        raise HTTPException(status_code=400, detail="Transaction not approved")
    create_transaction(
        db,
        user_id,
        float(my_approve_topup.amount),  # type: ignore
        "promptpay",
        "Topup approved",
    )
    user_activity = f"User {current_user.email} approved topup {topup_id}"
    create_log_info(
        db, str(current_user.id), user_activity, topup_id=topup_id, type_log="topup"
    )
    return {"message": "Transaction approved successfully"}


@router.get("/get_image/{topup_id}")
async def get_topup_image_by_id(
    topup_id: str,
    db: Session = Depends(get_db),
):
    try:
        topup = get_topup_by_id(db, topup_id)
        if not topup:
            raise HTTPException(status_code=404, detail="Topup not found")
        image = base64.b64decode(str(topup.image_base64))
        return Response(content=image, media_type="image/png")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Invalid image base64") from e
