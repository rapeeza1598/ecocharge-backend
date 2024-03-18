from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.user import change_password_current_user, get_user_by_id, update_user
from app.database import get_db
from app.schemas.user import User, changePassword, updateUser
from app.core.security import get_current_user

router = APIRouter(
    prefix="/user",
    tags=["User"],
    # default_response_class=Depends(get_current_user),
    responses={404: {"description": "Not found"}},
)

@router.get("/me",response_model=User)
async def read_users_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> User:
    return current_user

@router.get('/{user_id}',response_model=User)
async def read_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if user := get_user_by_id(db, user_id):
            return user
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail="User not found") from e
    
@router.post("/password")
async def change_password(
    new_password: changePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if new_password.password != new_password.confirmPassword:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        if change_password_current_user(db, str(current_user.id), new_password.password):
            return {"message": "Password updated successfully"}
        else:
            raise HTTPException(status_code=400, detail="Password not updated")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Password not updated") from e
    
@router.put("/me")
async def update_current_user(
    user: updateUser,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_user(db, str(current_user.id), user)

