from pydantic import BaseModel


class Token(BaseModel):
    token: str
    email: str

class setNewPassword(BaseModel):
    token: str
    new_password: str