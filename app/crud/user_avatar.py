from sqlalchemy.orm import Session

from app.models.user_avatars import UserAvatar
from app.schemas.user_avatar import UploadUserAvatar

def get_user_avatar(db: Session, user_id: str):
    return db.query(UserAvatar).filter(UserAvatar.userId == user_id).first() # type: ignore

def create_user_avatar(db: Session, user_avatar: UploadUserAvatar):
    db_user_avatar = UserAvatar(
        userId=user_avatar.user_id,
        avatar=user_avatar.avatar_img_b64
    )
    try:
        db.add(db_user_avatar)
        db.commit()
        db.refresh(db_user_avatar)
    except Exception as e:
        print(e)
        return None
    return db_user_avatar

def update_user_avatar(db: Session, user_id: str, avatar_img_b64: str):
    if (
        db_user_avatar := db.query(UserAvatar)
        .filter(UserAvatar.user_id == user_id) # type: ignore
        .first()
    ):
        setattr(db_user_avatar, "avatar_img_b64", avatar_img_b64)
        try:
            db.commit()
            db.refresh(db_user_avatar)
        except Exception as e:
            print(e)
            return None
        return db_user_avatar

def delete_user_avatar(db: Session, user_id: str):
    if (
        db_user_avatar := db.query(UserAvatar)
        .filter(UserAvatar.user_id == user_id) # type: ignore
        .first()
    ):
        try:
            db.delete(db_user_avatar)
            db.commit()
        except Exception as e:
            print(e)
            return None
        return db_user_avatar
    return None