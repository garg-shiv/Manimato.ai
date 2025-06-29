"""Shared dependencies for dependency injection."""

from functools import lru_cache
# from app.services.chat_service import ChatService
from app.services.chain_manager import ChainManager


# @lru_cache()
# def get_chat_service() -> ChatService:
#     """Get chat service instance."""
#     return ChatService()


@lru_cache()
def get_chain_manager() -> ChainManager:
    """Get chain manager instance."""
    return ChainManager()
