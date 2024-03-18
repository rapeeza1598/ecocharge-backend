from app.models.transactions import Transaction
from sqlalchemy.orm import Session


def create_transaction(db: Session, transaction: Transaction):
    db_transaction = Transaction(**transaction.dict())
    try:
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
    except Exception as e:
        print(e)
        return None
    return db_transaction


def get_transactions(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Transaction).offset(skip).limit(limit).all()


def get_transaction_by_user_id(db: Session, user_id: str):
    return db.query(Transaction).filter(Transaction.userId == user_id).all()  # type: ignore


def get_transaction_by_id(db: Session, transaction_id: str):
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()  # type: ignore


def get_transaction_by_station_id(db: Session, station_id: str):
    return (
        db.query(Transaction)
        .filter(Transaction.stationId == station_id)
        .all()
    )
