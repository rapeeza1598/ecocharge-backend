from pydantic import BaseModel


class UploadUserAvatar(BaseModel):
    avatar_img_b64: str