from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    message_id = Column(
        Integer,
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    message = relationship("Message", back_populates="prompt")
