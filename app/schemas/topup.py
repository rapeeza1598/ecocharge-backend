from pydantic import BaseModel


class TopupCreate(BaseModel):
    image_base64: str
    amount: float

class TopupImage(BaseModel):
    image: str

class TopupResponse(BaseModel):
    id: str
    userId: str
    amount: float
    status_approved: bool
    created_at: str
    firstName: str
    lastName: str
    email: str