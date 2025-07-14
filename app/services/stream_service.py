import logging
import os
import tempfile
from datetime import datetime
from typing import AsyncGenerator, Optional

import aiofiles
from schemas.inference import InferenceRequest
from services.cloud_service import CloudStorage
from sqlalchemy.orm import Session

from app.database.models import Code
from app.schemas.stream import ErrorMessages, StreamEvent, StreamMarkers
from app.services.chain_manager import ChainManager

logger = logging.getLogger(__name__)


class StreamService:
    """Service for handling AI streaming, file operations, and database updates"""

    def __init__(self, chain_manager: ChainManager, cloud_storage: CloudStorage):
        self.chain_manager = chain_manager
        self.cloud_storage = cloud_storage

    async def process_message_stream(
        self, message_id: int, prompt: str, db: Session
    ) -> AsyncGenerator[StreamEvent, None]:
        """
        Main streaming process that handles:
        1. AI code generation streaming
        2. File saving
        3. Cloud upload
        4. Database updates
        """
        code_chunks = []
        # Save code to file
        file_path = None
        try:
            # Stream AI response
            async for event in self._stream_ai_response(message_id, prompt):
                if event.type == "error":
                    yield event
                    return
                elif event.type == "code_chunk":
                    code_chunks.append(event.data)
                    yield event
                elif event.type == "ai_completed":
                    yield event
                    break

            # Process the complete code
            full_code = "".join(code_chunks)

            if not full_code.strip():
                yield StreamEvent(
                    type="error", data="No code generated", message_id=message_id
                )
                return

            try:
                file_path = await self._save_code_to_file(full_code, message_id)
                # yield StreamEvent(
                #     type="file_saved",
                #     data=f"Code saved to temporary file: {os.path.basename(file_path)}",
                #     message_id=message_id
                # )
            except Exception as e:
                logger.error(f"Failed to save file: {str(e)}")
                yield StreamEvent(
                    type="error", data="Failed to save file", message_id=message_id
                )
                # Still try to update database with code content
                await self._update_code_in_db(db, message_id, full_code)
                return

            # Upload to cloud
            cloud_url = None
            try:
                cloud_url = await self._upload_to_cloud(file_path)
                # yield StreamEvent(
                #     type="cloud_uploaded",
                #     data=f"File uploaded to cloud: {cloud_url}",
                #     message_id=message_id
                # )
            except Exception as e:
                logger.error(f"Failed to upload to cloud: {str(e)}")
                yield StreamEvent(
                    type="error", data="Failed to save File", message_id=message_id
                )
                # Continue with database update even if cloud upload fails

            # Update database
            try:
                await self._update_code_in_db(db, message_id, full_code, cloud_url)
                yield StreamEvent(
                    type="completed",
                    data="Process completed successfully",
                    message_id=message_id,
                )
            except Exception as e:
                logger.error(f"Failed to update database: {str(e)}")
                yield StreamEvent(
                    type="error", data="Failed to save File", message_id=message_id
                )
        except Exception as e:
            logger.error(f"Unexpected error in stream processing: {str(e)}")
            yield StreamEvent(
                type="error", data=f"Unexpected error: {str(e)}", message_id=message_id
            )
        finally:
            # Clean up temporary file
            if file_path:
                await self._cleanup_temp_file(file_path)

    async def _stream_ai_response(
        self, message_id: int, prompt: str
    ) -> AsyncGenerator[StreamEvent, None]:
        """Stream AI response and convert to StreamEvent objects"""
        try:
            request = InferenceRequest(prompt=prompt)
            stream = self.chain_manager.run_inference_stream(request)

            async for chunk in stream:
                if chunk == StreamMarkers.STREAM_END:
                    yield StreamEvent(
                        type="ai_completed",
                        data="AI streaming completed",
                        message_id=message_id,
                    )
                    break
                elif chunk.startswith(StreamMarkers.STREAM_ERROR):
                    error_msg = chunk[
                        len(StreamMarkers.STREAM_ERROR) :
                    ]  # Remove "__STREAM_ERROR__" prefix
                    logger.error(f"AI Error for message {message_id}: {error_msg}")
                    yield StreamEvent(
                        type="error",
                        data=ErrorMessages.GENERAL_ERROR,
                        message_id=message_id,
                    )
                    break
                else:
                    yield StreamEvent(
                        type="code_chunk", data=chunk, message_id=message_id
                    )

        except Exception as e:
            logger.error(f"AI streaming error: {str(e)}")
            yield StreamEvent(
                type="error",
                data=f"AI streaming error: {ErrorMessages.SYSTEM_ERROR}",
                message_id=message_id,
            )

    async def _save_code_to_file(self, code_content: str, message_id: int) -> str:
        """Save code to temporary file"""
        temp_dir = tempfile.gettempdir()
        filename = (
            f"manim_code_{message_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        )
        file_path = os.path.join(temp_dir, filename)

        async with aiofiles.open(file_path, "w") as f:
            await f.write(code_content)

        return file_path

    async def _upload_to_cloud(self, file_path: str) -> str:
        """Upload file to cloud storage"""
        logger.info("Uploading to cloud")
        return await self.cloud_storage.upload_file(file_path)

    async def _update_code_in_db(
        self,
        db: Session,
        message_id: int,
        code_content: str,
        file_url: Optional[str] = None,
    ):
        """Update or create code record in database"""
        # Check if code already exists
        existing_code = db.query(Code).filter(Code.message_id == message_id).first()

        if existing_code:
            if file_url:
                existing_code.public_id = file_url
            elif code_content:
                existing_code.code = code_content
        else:
            if file_url:
                code = Code(
                    message_id=message_id, code=code_content, public_id=file_url
                )
                db.add(code)
            else:
                code = Code(message_id=message_id, public_id=file_url)
                db.add(code)

        db.commit()

    async def _cleanup_temp_file(self, file_path: str):
        """Clean up temporary file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up temp file {file_path}: {str(e)}")
