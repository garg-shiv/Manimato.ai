from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")