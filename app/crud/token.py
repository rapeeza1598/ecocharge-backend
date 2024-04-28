from sqlalchemy.orm import Session
from app.models.tokens import Token

def create_token(db: Session, token:str, email:str):
    db_token = Token(token=token, email=email)
    try:
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
    except Exception as e:
        print(e)
        return None
    return db_token

def get_token(db: Session, token: str):
    if myToken := db.query(Token).filter(Token.token == token).first(): # type: ignore
        return myToken
    return None
    

def delete_token(db: Session, token: str):
    db.query(Token).filter(Token.token == token).delete()  # type: ignore
    try:
        db.commit()
    except Exception as e:
        print(e)
        return None
    return True

def update_token_by_email(db: Session, token: str, email: str):
    db_token = db.query(Token).filter(Token.email == email).first() # type: ignore
    if not db_token:
        return None
    setattr(db_token, "token", token)
    try:
        db.commit()
    except Exception as e:
        print(e)
        return None
    return True