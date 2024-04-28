from sqlalchemy import Column, String
from app.database import Base


class Token(Base):
    __tablename__ = "tokens"

    token = Column(String, index=True)
    email = Column(String, primary_key=True, index=True)

    def __init__(self, token, email):
        self.token = token
        self.email = email
