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
    query: str
    top_k: int = 5
    # wide-scan controls
    wide: bool = True
    target_confidence: float = 0.62
    max_passes: int = 3
    per_pass_retmax: int = 60
    mindate: Optional[int] = None       # preferred start year for pass 1
    fallback_mindate: int = 2010        # if pass 1 yields little/no material
    lang: Optional[str] = "en"
    types: Optional[List[str]] = None   # custom types for pass 1 (if provided)

class ExpandResponse(BaseModel):
    answer: str
    citations: list
    confidence: float
    # scan stats (cumulative across passes)
    found: int = 0      # items fetched (articles)
    added: int = 0      # chunks embedded & added to store
    skipped: int = 0
    passes: int = 0     # how many passes executed