import enum

from sqlalchemy import Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class SenderRole(enum.Enum):
    USER = "user"
    AI = "ai"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False
    )

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
