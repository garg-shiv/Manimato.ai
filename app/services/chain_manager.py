"""Chain manager for LangChain operations."""

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from app.schemas.inference import InferenceRequest, InferenceResponse
from app.core.llm_provider import llm_provider
from app.core.logger import logger


class ChainManager:
    """Manager for LangChain operations."""
    
    def __init__(self):
        self.llm = llm_provider.llm
        self._chains = {}
    
    async def run_inference(self, request: InferenceRequest) -> InferenceResponse:
        """Run inference using LangChain."""
        try:
            logger.info(f"Running inference with prompt: {request.prompt[:100]}...")
            
            # Create or get chain
            chain = self._get_or_create_chain(request.chain_type)
            
            # Run chain
            result = await chain.arun(
                input_text=request.prompt,
                **request.parameters
            )
            
            response = InferenceResponse(
                result=result,
                chain_type=request.chain_type
            )
            
            logger.info("Inference completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error running inference: {str(e)}")
            raise
    
    def _get_or_create_chain(self, chain_type: str) -> LLMChain:
        """Get or create a chain by type."""
        if chain_type not in self._chains:
            self._chains[chain_type] = self._create_chain(chain_type)
        return self._chains[chain_type]
    
    def _create_chain(self, chain_type: str) -> LLMChain:
        """Create a new chain."""
        templates = {
            "simple": "Answer the following question: {input_text}",
            "analysis": "Analyze the following text in detail: {input_text}",
            "summary": "Provide a concise summary of: {input_text}"
        }
        
        template = templates.get(chain_type, templates["simple"])
        prompt = PromptTemplate(template=template, input_variables=["input_text"])
        
        return LLMChain(llm=self.llm, prompt=prompt)
