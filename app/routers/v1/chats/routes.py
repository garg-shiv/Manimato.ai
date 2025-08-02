from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from database.session import get_db

from schemas.chats import ChatCreateRequest
from services.chat_service import ChatService

router = APIRouter(prefix="/chats", tags=["chats"])
chat_service = ChatService()


@router.post("/")
async def create_chat(req:ChatCreateRequest, db:Session=Depends(get_db)):
  """Create a chat with initial Message"""
  result = await chat_service.create_chat(req.initialMessage, db)
  return Response(content=result, media_type="application/json")

