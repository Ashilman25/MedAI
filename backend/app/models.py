from pydantic import BaseModel, Field
from typing import List, Optional

class Citation(BaseModel):
    title: str
    url: str
    snippet: str

class AskRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000)
    top_k: int = Field(5, ge=1, le=50)

class AskResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence: float

class IngestResponse(BaseModel):
    ok: bool
    added: int
    skipped: int

class ExpandRequest(BaseModel):

    query: Optional[str] = Field(None, max_length=2000)
    query_terms: Optional[List[str]] = None
    intent: Optional[str] = None  

    top_k: int = Field(5, ge=1, le=50)

    wide: bool = True
    target_confidence: float = Field(0.62, ge=0.0, le=1.0)
    max_passes: int = Field(3, ge=1, le=5)
    per_pass_retmax: int = Field(60, ge=10, le=500)
    mindate: Optional[int] = None       
    fallback_mindate: int = 2010        
    lang: Optional[str] = "en"
    types: Optional[List[str]] = None

class ExpandResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence: float

    found: int = 0      # items fetched (articles)
    added: int = 0      # chunks embedded & added to store
    skipped: int = 0
    passes: int = 0     # how many passes executed