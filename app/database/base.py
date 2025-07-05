from sqlalchemy.orm import declarative_base

Base = declarative_base()

# for alembic autogeneration
from database.models.chat import Chat
from database.models.user import User
from database.models.message import Message
from database.models.code import Code
from database.models.prompt import Prompt
from database.models.video import Video
