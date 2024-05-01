import base64
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.crud.user import get_user_by_id
from app.crud.user_avatar import (
    create_user_avatar,
    delete_user_avatar,
    get_user_avatar,
    update_user_avatar,
)
from app.database import get_db
from app.schemas.user import User
from app.schemas.user_avatar import UploadUserAvatar

router = APIRouter(
    prefix="/image",
    tags=["Image"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_user_avatar_image(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if (user_avatar := get_user_by_id(db, str(current_user.id))) is None:
            raise HTTPException(status_code=404, detail="User not found")
        avatar = get_user_avatar(db, str(current_user.id))
        if avatar is None:
            raise HTTPException(status_code=404, detail="Image not found")
        image = base64.b64decode(str(avatar.avatar))
        return Response(content=image, media_type="image/png")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="Image not found") from e


@router.post("/")
async def post_user_avatar_image(
    user_avatar: UploadUserAvatar,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if get_user_by_id(db, str(current_user.id)) is None:
            raise HTTPException(status_code=404, detail="User not found")
        if len(user_avatar.avatar_img_b64) > 4 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image size too large")
        base64.b64decode(user_avatar.avatar_img_b64)
        if get_user_avatar(db, str(current_user.id)):
            update_user_avatar(db, str(current_user.id), user_avatar.avatar_img_b64)
            return {"message": "Image updated"}
        if create_user_avatar(db, str(current_user.id),user_avatar):
            return {"message": "Image uploaded"}
        raise HTTPException(status_code=400, detail="Image already image updated")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Image not uploaded") from e


@router.delete("/")
async def delete_user_avatar_image(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if get_user_by_id(db, str(current_user.id)) is None:
            raise HTTPException(status_code=404, detail="User not found")
        if delete_user_avatar(db, str(current_user.id)):
            return {"message": "Image deleted"}
        else:
            raise HTTPException(status_code=400, detail="Image not deleted")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Image not deleted") from e
