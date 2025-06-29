from pydantic import BaseModel

class InferenceRequest(BaseModel):
    prompt: str

class InferenceResponse(BaseModel):
    result: str

# Removed redundant Prompt model since InferenceRequest is used instead.
