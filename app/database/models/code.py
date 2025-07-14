from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Code(Base):
    __tablename__ = "codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[str] = mapped_column(Text, nullable=False)
    message_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("messages.id", ondelete="CASCADE"), unique=True
    )
    code: Mapped[str | None] = mapped_column(Text, nullable=True)

    # relationships
    message = relationship("Message", back_populates="code")
