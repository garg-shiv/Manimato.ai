from sqlalchemy.orm import declarative_base

Base = declarative_base()

# for alembic autogeneration
from app.database.models import user, chat, message, prompt, code ,video