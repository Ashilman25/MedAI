from pydantic import BaseModel, Field
from typing import List

class Citation(BaseModel):
    title: str
    url: str
    snippet: str

class AskRequest(BaseModel):
    query: str = Field(..., min_length=2)
    top_k: int = 5

class AskResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence: float

class IngestResponse(BaseModel):
    ok: bool
    added: int
    skipped: int
