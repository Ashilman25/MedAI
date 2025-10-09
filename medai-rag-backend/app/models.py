from pydantic import BaseModel, Field
from typing import List, Optional
from pydantic import BaseModel

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

class ExpandRequest(BaseModel):

    query: Optional[str] = None
    query_terms: Optional[List[str]] = None
    intent: Optional[str] = None  

    top_k: int = 5

    wide: bool = True
    target_confidence: float = 0.62
    max_passes: int = 3
    per_pass_retmax: int = 60
    mindate: Optional[int] = None       
    fallback_mindate: int = 2010        
    lang: Optional[str] = "en"
    types: Optional[List[str]] = None   
    owner_uid: Optional[str] = None

class ExpandResponse(BaseModel):
    answer: str
    citations: list
    confidence: float

    found: int = 0      # items fetched (articles)
    added: int = 0      # chunks embedded & added to store
    skipped: int = 0
    passes: int = 0     # how many passes executed