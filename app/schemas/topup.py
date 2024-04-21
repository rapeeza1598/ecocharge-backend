from pydantic import BaseModel


class TopupCreate(BaseModel):
    image_base64: str
    amount: float

class TopupImage(BaseModel):
    image: str