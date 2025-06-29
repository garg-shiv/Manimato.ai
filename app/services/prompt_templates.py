"""Prompt templates for LLM interactions."""

from langchain.prompts import PromptTemplate


class PromptTemplates:
    """Collection of prompt templates."""
    
    def __init__(self):
        self.chat_template = PromptTemplate(
            template="""You are a helpful AI assistant. Please respond to the user's message based on the conversation history.

Conversation History:
{conversation_history}

Please provide a helpful and accurate response.""",
            input_variables=["conversation_history"]
        )
        
        self.system_template = PromptTemplate(
            template="""You are an AI assistant with the following characteristics:
- Helpful and informative
- Accurate and truthful
- Respectful and professional

User Query: {query}

Response:""",
            input_variables=["query"]
        )
    
    def create_chat_prompt(self, conversation_history: str) -> str:
        """Create a chat prompt from conversation history."""
        return self.chat_template.format(conversation_history=conversation_history)
    
    def create_system_prompt(self, query: str) -> str:
        """Create a system prompt for a query."""
        return self.system_template.format(query=query)
    
    def create_custom_prompt(self, template: str, **kwargs) -> str:
        """Create a custom prompt from template and variables."""
        prompt_template = PromptTemplate(
            template=template,
            input_variables=list(kwargs.keys())
        )
        return prompt_template.format(**kwargs)
