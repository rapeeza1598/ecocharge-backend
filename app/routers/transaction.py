from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.crud.transaction import get_transaction_by_user_id, get_transactions
from app.crud.user import get_user_by_id
from app.database import get_db
from app.schemas.transaction import Transaction, responseTransaction
from app.schemas.user import User


router = APIRouter(
    prefix="/transaction",
    tags=["Transaction"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[responseTransaction])
async def read_transactions(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # if current_user.role not in ["superadmin"]:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    users = get_user_by_id(db, str(current_user.id))
    transactions = get_transaction_by_user_id(db, str(current_user.id))
    # map user to transaction
    for transaction in transactions:
        if users is not None:
            transaction.firstName = users.firstName
            transaction.lastName = users.lastName
            transaction.email = users.email
    return transactions

@router.get("/{user_id}", response_model=list[responseTransaction])
async def read_transactions_by_user_id(
    user_id: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["superadmin"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    users = get_user_by_id(db, user_id)
    transactions = get_transaction_by_user_id(db, user_id)
    # map user to transaction
    for transaction in transactions:
        if users is not None:
            transaction.firstName = users.firstName
            transaction.lastName = users.lastName
            transaction.email = users.email
    return transactions
