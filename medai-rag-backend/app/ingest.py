import os, csv, argparse, json
from typing import List, Dict, Any
from .config import get_settings
from .logging_config import info, warn
from .utils.text import clean_text, chunk_text
from .utils.pdf import extract_pdf_text
from .vectorstore.faiss_store import FaissStore
from .rag import get_embedder, provider_signature

def read_file_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extract_pdf_text(path)
    elif ext in [".txt", ".md"]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    elif ext == ".csv":
        out = []
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            r = csv.reader(f)
            out.extend(" | ".join(row) for row in r)
        return "\n".join(out)
    warn(f"Unsupported file type: {ext}. Skipping {path}")
    return ""

def ingest_paths(paths: List[str]) -> Dict[str, Any]:
    s = get_settings()
    embedder = get_embedder()
    store = FaissStore(s.STORAGE_DIR, embedder.dim, provider_signature(embedder))
    added = 0; skipped = 0
    for p in paths:
        if not os.path.exists(p):
            warn(f"Missing: {p}"); skipped += 1; continue
        raw = read_file_text(p)
        txt = clean_text(raw)
        if not txt: skipped += 1; continue
        title = None; url = None
        try:
            lines = raw.strip().splitlines()
            for ln in lines[:4]:
                if ln.lower().startswith("title:"): title = ln.split(":",1)[1].strip()
                if ln.lower().startswith("url:"): url = ln.split(":",1)[1].strip()
        except Exception: pass
        if not title: title = os.path.basename(p)
        if not url: url = f"file://{os.path.abspath(p)}"
        chunks = chunk_text(txt, chunk_size=1200, overlap=200)
        if not chunks: skipped += 1; continue
        embs = embedder.encode(chunks)
        metadatas = [ {"title": title, "url": url, "snippet": c[:240], "source_path": os.path.abspath(p)} for c in chunks ]
        store.add(embs, metadatas); added += len(chunks)
    info(f"Ingested: added={added}, skipped={skipped}, total={FaissStore(s.STORAGE_DIR, embedder.dim, provider_signature(embedder)).size()}")
    return {"ok": True, "added": added, "skipped": skipped}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", action="append", help="file or directory to ingest", required=True)
    args = ap.parse_args()
    targets = []
    for p in args.path:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in files: targets.append(os.path.join(root, f))
        else:
            targets.append(p)
    res = ingest_paths(targets)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
