from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.topups import Topups
from app.models.users import User
from app.schemas.topup import TopupCreate


def create_topup(db: Session,userId:str, topup: TopupCreate):
    db_topup = Topups(
        userId=userId,
        image_base64=topup.image_base64,
        amount=topup.amount,
    )
    db.add(db_topup)
    db.commit()
    db.refresh(db_topup)
    return db_topup


def get_topups(
    db: Session, skip: int = 0, limit: int = 10, status_approved: bool = False
):
    return (
        db.query(Topups)
        .filter(Topups.status_approved == status_approved)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_topup_by_user_id(db: Session, user_id: str):
    return db.query(Topups).filter(Topups.userId == user_id).all()  # type: ignore

def get_topup_by_id(db: Session, topup_id: str):
    return db.query(Topups).filter(Topups.id == topup_id).first()  # type: ignore

def approve_topup(db: Session, topup_id: str):
    db_topup: Topups | None = db.query(Topups).filter(Topups.id == topup_id).first()  # type: ignore
    db_user = db.query(User).filter(User.id == db_topup.userId).first() # type: ignore
    if db_user is not None and db_topup is not None and db_topup.status_approved is False:
        try:
            if db_topup.status_approved is True:
                return None
            setattr(db_topup, "status_approved", True)
            db.commit()
            updated_balance = db_user.balance + Decimal(db_topup.amount) # type: ignore
            setattr(db_user, "balance", updated_balance)
            db.commit()
            db.refresh(db_topup)
        except Exception as e:
            print(e)
            return None
    return db_topup


def delete_topup(db: Session, topup_id: str):
    db_topup: Topups | None = db.query(Topups).filter(Topups.id == topup_id).first()  # type: ignore
    db.delete(db_topup)
    db.commit()
    return db_topup
