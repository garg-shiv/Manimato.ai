
from pydantic import BaseModel

from database.models.chat import Chat


class ChatCreateRequest(BaseModel):
  initialMessage: str

