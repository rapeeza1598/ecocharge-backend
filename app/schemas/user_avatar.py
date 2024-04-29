from pydantic import BaseModel


class UploadUserAvatar(BaseModel):
    user_id: str
    avatar_img_b64: str