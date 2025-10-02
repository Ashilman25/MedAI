import re
from typing import List
def clean_text(s: str) -> str:
    s = s.replace('\x00', ' ').replace('\u0000', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s
def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> List[str]:
    text = text.strip()
    if not text: return []
    chunks = []; start = 0; n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end]; chunks.append(chunk)
        if end == n: break
        start = max(0, end - overlap)
    return chunks
