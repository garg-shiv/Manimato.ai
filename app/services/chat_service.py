"""Chat service for handling chat logic."""

from typing import List
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage
from app.core.llm_provider import llm_provider
from app.services.prompt_templates import PromptTemplates
from app.core.logger import logger


class ChatService:
    """Service for handling chat operations."""
    
    def __init__(self):
        self.llm = llm_provider.llm
        self.prompt_templates = PromptTemplates()
    
    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        """Process a chat request."""
        try:
            logger.info(f"Processing chat request with {len(request.messages)} messages")
            
            # Format conversation history
            formatted_messages = self._format_messages(request.messages)
            
            # Create prompt
            prompt = self.prompt_templates.create_chat_prompt(formatted_messages)
            
            # Get response from LLM
            response = await self.llm.ainvoke(prompt)
            
            # Create response
            chat_response = ChatResponse(
                message=response.content,
                conversation_id=request.conversation_id
            )
            
            logger.info("Chat request processed successfully")
            return chat_response
            
        except Exception as e:
            logger.error(f"Error processing chat request: {str(e)}")
            raise
    
    def _format_messages(self, messages: List[ChatMessage]) -> str:
        """Format chat messages for the prompt."""
        formatted = []
        for msg in messages:
            role = "Human" if msg.role == "user" else "Assistant"
            formatted.append(f"{role}: {msg.content}")
        return "\n".join(formatted)
