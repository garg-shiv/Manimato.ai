from tokenize import String

from database.base import Base
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True)
    message_id = Column(
        Integer, ForeignKey("messages.id", ondelete="CASCADE"), unique=True
    )
    public_id = Column(String, nullable=False)

    message = relationship("Message", back_populates="video")
