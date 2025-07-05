import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database.base import Base


class SenderRole(enum.Enum):
    USER = "user"
    AI = "ai"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(
        Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False
    )
    sender = Column(Enum(SenderRole), nullable=False)

    # Relationships
    chat = relationship("Chat", back_populates="messages")
    prompt = relationship(
        "Prompt", uselist=False, back_populates="message", cascade="all, delete-orphan"
    )
    code = relationship(
        "Code", uselist=False, back_populates="message", cascade="all, delete-orphan"
    )
    video = relationship(
        "Video", uselist=False, back_populates="message", cascade="all, delete-orphan"
    )
