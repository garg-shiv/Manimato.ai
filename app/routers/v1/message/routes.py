import json
import logging
from typing import AsyncGenerator

from database.session import get_db
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from services.cloud_service import CloudStorage
from sqlalchemy.orm import Session

from app.schemas.stream import MessageResponse, PromptRequest, StreamEvent
from app.services.chain_manager import ChainManager
from app.services.message_service import MessageService
from app.services.stream_service import StreamService

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/messages", tags=["messages"])

chain_manager = ChainManager()
message_service = MessageService()
# TODO: implement this
cloud_storage = CloudStorage("cloudinary")
stream_service = StreamService(chain_manager, cloud_storage)


@router.post("/create", response_model=MessageResponse)
async def create_message(request: PromptRequest, db: Session = Depends(get_db)):
    """Create message in database and retur message ID"""

    try:
        response = message_service.create_message(db, request.chat_id, request.prompt)
        logger.info(f"Created message {response.message_id} for chat {request.chat_id}")
        return response
    except Exception as e:
        logger.error(f"Failed to create message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create message")


@router.post("/{message_id}/stream-code")
async def stream_ai_response(message_id: int, db: Session = Depends(get_db)):
    """Stream AI response for a message"""

    try:
        message = message_service.get_message_with_prompt(db, message_id)
        prompt_text = message.prompt.content

        logger.info(f"Starting stream for message {message_id}")

        async def event_stream() -> AsyncGenerator[str, None]:
            try:
                async for event in stream_service.process_message_stream(
                    message_id, prompt_text, db
                ):
                    event_data = event.model_dump()
                    yield f"data: {json.dumps(event_data)}\n\n"

                    if event.type in ["completed", "error"]:
                        logger.info(f"message {message_id}-{event.type}:{event.data}")
            except Exception as e:
                logger.error(f"Stream error for message {message_id}:{str(e)}")
                error_event = StreamEvent(
                    type="error", data="Internal Server Error", message_id=message_id
                ).model_dump()
                yield f"data: {json.dumps(error_event)}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    except ValueError as e:
        logger.error(f"Message not found: {str(e)}")
        raise HTTPException(status_code=404, detail="Message not found")
    except Exception as e:
        logger.error(f"Failed to start stream: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start Stream")
