from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    public_id: Mapped[str] = mapped_column(String, nullable=False)

    message = relationship("Message", back_populates="video")
