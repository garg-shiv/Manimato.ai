from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database.base import Base


class Code(Base):
    __tablename__ = "codes"

    id = Column(Integer, primary_key=True)
    public_id = Column(Text, nullable=False)
    message_id = Column(
        Integer, ForeignKey("messages.id", ondelete="CASCADE"), unique=True
    )

    # relationships
    message = relationship("Message", back_populates="code")
