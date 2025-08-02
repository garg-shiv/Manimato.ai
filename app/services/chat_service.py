from fastapi import Depends
from sqlalchemy.orm import Session

from database.models.chat import Chat
from database.models.message import Message
from database.models.prompt import Prompt
from database.session import get_db

class ChatService:
  def __init__(self):
    pass
  
  async def create_chat(self, initialMessage:str, db:Session=Depends(get_db)):
    newChat = Chat()
    db.add(newChat)
    db.flush()

    newMessage = Message()
    newMessage.prompt = Prompt(content=initialMessage)
    newMessage.chat = newChat
    db.add(newMessage)
    db.commit()

    result  = {
      "chat_id": newChat.id,
      "message_id": newMessage.id,
      "initial_message": initialMessage
    }
    return result