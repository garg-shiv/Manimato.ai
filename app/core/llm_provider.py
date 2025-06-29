"""LLM provider configuration for Gemini/LangChain."""

from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import BaseLanguageModel
from app.core.config import settings
from app.core.logger import logger


class LLMProvider:
    """LLM provider for managing Gemini model."""
    
    def __init__(self):
        self._llm: Optional[BaseLanguageModel] = None
    
    @property
    def llm(self) -> BaseLanguageModel:
        """Get or create LLM instance."""
        if self._llm is None:
            self._llm = self._create_llm()
        return self._llm
    
    def _create_llm(self) -> BaseLanguageModel:
        """Create Gemini LLM instance."""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        
        logger.info(f"Initializing Gemini model: {settings.LLM_MODEL}")
        
        return ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7,
            convert_system_message_to_human=True
        )


# Global LLM provider instance
llm_provider = LLMProvider()
