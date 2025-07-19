import json
import logging
import urllib.request
from typing import AsyncGenerator

from app.database.session import get_db
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.services.cloud_service import CloudStorage
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Code
from app.schemas.stream import MessageResponse, PromptRequest, StreamEvent
from app.services import render_service
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



@router.post("/{message_id}/render-video")
async def render_video(message_id: int, db: Session = Depends(get_db)):
    """Fetch code by message_id, render it via Manim, and upload result"""

    # Step 1: Fetch code metadata
    code_obj = db.execute(
        select(Code).where(Code.message_id == message_id)
    ).scalar_one_or_none()

    if not code_obj:
        raise HTTPException(status_code=404, detail="No code found for this message")

    public_id = code_obj.public_id
    local_path = f"/tmp/{public_id}.py"

    # Step 2: Get secure URL
    try:
        secure_url = await cloud_storage.get_secure_url(public_id, format="py", resource_type="raw")
    except Exception as e:
        logger.error(f"Failed to generate secure URL: {e}")
        raise HTTPException(status_code=500, detail="Cloudinary URL generation failed")

    # Step 3: Download file
    try:
        urllib.request.urlretrieve(secure_url, local_path)
    except Exception as e:
        logger.error(f"Failed to download file: {e}")
        raise HTTPException(status_code=500, detail="Failed to download file")

    # Step 4: Read code
    try:
        with open(local_path, "r") as f:
            script = f.read()
    except Exception as e:
        logger.error(f"Failed to read downloaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to read downloaded file")

    # Step 5: Render video
    try:
        rendered_path = await render_service.render_manim_script(script)
    except Exception as e:
        logger.error(f"Rendering failed: {e}")
        raise HTTPException(status_code=500, detail="Video rendering failed")

    
    # Step 6: Upload rendered video to Cloudinary
    try:
        video_public_id = await cloud_storage.upload_file(rendered_path)
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload to cloud failed")

    # Step 7: Return Cloudinary video public_id
    return {
        "message_id": message_id,
        "video_public_id": video_public_id
    }