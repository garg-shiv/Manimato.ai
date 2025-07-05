from app.database.base import Base
from sqlalchemy import Column, ForeignKey, Integer, Text


class Code(Base):
    __tablename__ = "codes"

    id = Column(Integer, primary_key=True)
    public_id = Column(Text, nullable=False)
    message_id = Column(
        Integer, ForeignKey("messages.id", ondelete="CASCADE"), unique=True
    )

    # relationships
    message = Column("Message", back_populates="code")
