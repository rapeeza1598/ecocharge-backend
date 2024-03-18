from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.crud.transaction import create_transaction, get_transactions
from app.crud.user import get_user_by_id
from app.database import get_db
from app.schemas.user import User
from decimal import Decimal

router = APIRouter(
    prefix="/top_up",
    tags=["Top up"],
    responses={404: {"description": "Not found"}},
)


# @router.put("/users/{user_id}/topup")
# async def topup_user_balance(
#     user_id: str,
#     amount: float,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     if current_user.role not in ["superadmin"]:
#         raise HTTPException(status_code=401, detail="Unauthorized")
#     user = get_user_by_id(db, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     amount_decimal = Decimal(amount)
#     # save transaction
#     transaction = create_transaction(
#         userId=user_id,
#         amount=float(amount_decimal),
#         transactionType="topup",
#         description="User balance topup",
#     )
#     db_transaction = create_transaction(db, transaction)
#     if not db_transaction:
#         raise HTTPException(status_code=400, detail="Transaction not created")
#     user.balance += amount_decimal # type: ignore
#     db.commit()
#     return {"message": "User balance updated successfully"}