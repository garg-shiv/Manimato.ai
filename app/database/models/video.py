from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True)
    message_id = Column(
        Integer, ForeignKey("messages.id", ondelete="CASCADE"),nullable=False, unique=True
    )
    public_id = Column(String, nullable=False)

    message = relationship("Message", back_populates="video")
