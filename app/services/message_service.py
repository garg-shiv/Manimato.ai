import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.models import Message, Prompt
from app.schemas.stream import MessageResponse

logger = logging.getLogger(__name__)


class MessageService:
    """Service for handling message-related database operations"""

    def __init__(self):
        pass

    def create_message(
        self, db: Session, chat_id: int, prompt_text: str
    ) -> MessageResponse:
        """Create message and prompt in database"""
        try:
            # Create message
            message = Message(
                chat_id=chat_id,
            )
            db.add(message)
            db.flush()  # Get the ID without committing

            # Create prompt
            prompt = Prompt(message_id=message.id, content=prompt_text)
            db.add(prompt)
            db.commit()
            db.refresh(message)

            logger.info(f"Created message {message.id} for chat {chat_id}")

            return MessageResponse(message_id=message.id, status="created")

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating message: {str(e)}")
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error creating message: {str(e)}")
            raise

    def get_message_with_prompt(self, db: Session, message_id: int) -> Message:
        """Get message with its prompt"""
        try:
            message = db.query(Message).filter(Message.id == message_id).first()
            if not message:
                raise ValueError(f"Message {message_id} not found")

            if not message.prompt:
                raise ValueError(f"Message {message_id} has no prompt")

            return message

        except Exception as e:
            logger.error(f"Error getting message {message_id}: {str(e)}")
            raise

    def get_message_code(self, db: Session, message_id: int) -> str:
        """Get the code content for a message"""
        try:
            message = db.query(Message).filter(Message.id == message_id).first()
            if not message:
                raise ValueError(f"Message {message_id} not found")

            if not message.code:
                raise ValueError(f"Message {message_id} has no code")

            return message.code.content

        except Exception as e:
            logger.error(f"Error getting code for message {message_id}: {str(e)}")
            raise

    def message_exists(self, db: Session, message_id: int) -> bool:
        """Check if a message exists"""
        try:
            return (
                db.query(Message).filter(Message.id == message_id).first() is not None
            )
        except Exception as e:
            logger.error(f"Error checking message existence {message_id}: {str(e)}")
            return False
