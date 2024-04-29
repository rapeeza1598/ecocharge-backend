from sqlalchemy import Column, ForeignKey, String
from app.database import Base

class UserAvatar(Base):
    __tablename__ = "user_avatars"

    userId = Column(String, ForeignKey("users.id"), primary_key=True)
    avatar = Column(String)

    def __init__(self, userId, avatar):
        self.userId = userId
        self.avatar = avatar