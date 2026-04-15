import os
import re
import uuid
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Depends, Request, HTTPException
from ..config import get_settings
from ..models import IngestResponse
from ..ingest import ingest_paths
from ..rag import get_store
from ..dependencies import limiter, get_current_uid, check_daily_limit

router = APIRouter()

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB per file


def _safe_filename(original: str) -> str:
    """Sanitize an uploaded filename to prevent path-traversal attacks.

    Strips directory components, replaces unsafe characters, and prepends a
    short random hex prefix so collisions are nearly impossible.
    """
    base = os.path.basename(original)
    base = re.sub(r'[^\w.\-]', '_', base)
    if not base or base in (".", ".."):
        base = "upload"
    return f"{uuid.uuid4().hex[:8]}_{base}"


@router.post("/ingest", response_model=IngestResponse)
@limiter.limit("10/minute")
async def ingest(request: Request, files: List[UploadFile] = File(...), uid: Optional[str] = Depends(get_current_uid)):
    if not uid:
        raise HTTPException(status_code=401, detail="Sign-in required")
    check_daily_limit(uid, "ingest")
    s = get_settings()
    upload_dir = os.path.join(s.STORAGE_DIR, "_uploads")
    os.makedirs(upload_dir, exist_ok=True)
    upload_real = os.path.realpath(upload_dir)
    paths = []
    for f in files:
        safe_name = _safe_filename(f.filename or "upload")
        dest = os.path.join(upload_dir, safe_name)
        if not os.path.realpath(dest).startswith(upload_real + os.sep):
            raise HTTPException(status_code=400, detail=f"Invalid filename: {f.filename!r}")
        content = await f.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"File '{f.filename}' exceeds 25MB limit")
        with open(dest, "wb") as out:
            out.write(content)
        paths.append(dest)
    res = ingest_paths(paths, owner_uid=uid)
    return IngestResponse(**res)


@router.get("/documents")
@limiter.limit("60/minute")
def list_docs(request: Request, uid: Optional[str] = Depends(get_current_uid)):
    """
    List documents indexed.

    - If uid provided: return docs owned by uid OR global docs (no owner_uids).
    - If uid not provided: return only global docs.
    """
    store = get_store()

    try:
        docs = []
        for md in getattr(store, "_meta", []):
            owners = md.get("owner_uids") or []
            if isinstance(owners, str):
                owners = [owners]

            if uid:
                if owners and uid not in owners:
                    continue
            else:
                if owners:
                    continue

            scope = "global" if not owners else ("mine" if (uid and uid in owners) else "private")

            docs.append({
                "title": md.get("title"),
                "url": md.get("url"),
                "source": md.get("source", "unknown"),
                "pmid": md.get("pmid", None),
                "journal": md.get("journal", None),
                "year": md.get("year", None),
                "snippet": (md.get("snippet", "") or "")[:180],
                "owner_scope": scope,
            })
        return {"count": len(docs), "docs": docs}
    except Exception as e:
        return {"error": str(e)}
