# app/ingest.py
import os, csv, argparse, json, time
from typing import List, Dict, Any, Tuple, Optional

from .config import get_settings
from .logging_config import info, warn
from .utils.text import clean_text, chunk_text
from .utils.pdf import extract_pdf_text
from .vectorstore.faiss_store import FaissStore
from .rag import get_embedder, provider_signature


# ----------------------------
# Local files (existing logic)
# ----------------------------
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

    added = 0
    skipped = 0

    for p in paths:
        if not os.path.exists(p):
            warn(f"Missing: {p}")
            skipped += 1
            continue

        raw = read_file_text(p)
        txt = clean_text(raw)
        if not txt:
            skipped += 1
            continue

        title = None
        url = None
        try:
            lines = raw.strip().splitlines()
            for ln in lines[:4]:
                if ln.lower().startswith("title:"):
                    title = ln.split(":", 1)[1].strip()
                if ln.lower().startswith("url:"):
                    url = ln.split(":", 1)[1].strip()
        except Exception:
            pass

        if not title:
            title = os.path.basename(p)
        if not url:
            url = f"file://{os.path.abspath(p)}"

        chunks = chunk_text(txt, chunk_size=1200, overlap=200)
        if not chunks:
            skipped += 1
            continue

        embs = embedder.encode(chunks)
        metadatas = [
            {
                "title": title,
                "url": url,
                "snippet": c[:240],
                "source_path": os.path.abspath(p),
                "source": "local",
            }
            for c in chunks
        ]
        store.add(embs, metadatas)
        added += len(chunks)

    info(
        f"Ingested (local): added={added}, skipped={skipped}, total={FaissStore(s.STORAGE_DIR, embedder.dim, provider_signature(embedder)).size()}"
    )
    return {"ok": True, "added": added, "skipped": skipped}


# ----------------------------
# PubMed ingestion (new)
# ----------------------------
def _abstract_to_text(abstract_obj) -> str:
    """
    AbstractText in Entrez XML can be:
      - a single string
      - a list of strings
      - a list of dict-like objects with 'Label' + text
    This normalizes it to plain text.
    """
    if not abstract_obj:
        return ""
    try:
        if isinstance(abstract_obj, str):
            return abstract_obj
        if isinstance(abstract_obj, list):
            parts = []
            for x in abstract_obj:
                if isinstance(x, str):
                    parts.append(x)
                else:
                    # dict-like (e.g., {'#text': 'text', 'Label': 'Methods'})
                    txt = ""
                    # Common shapes in Entrez.read():
                    # - {'Label': '...', 'attributes': {}, 'text': '...'}
                    # - or an element with .title() / .__str__()
                    for key in ["text", "#text"]:
                        if isinstance(x, dict) and key in x and isinstance(x[key], str):
                            txt = x[key]
                            break
                    if not txt:
                        txt = str(x)
                    label = ""
                    if isinstance(x, dict) and "Label" in x and x["Label"]:
                        label = f"{x['Label']}: "
                    parts.append(f"{label}{txt}")
            return " ".join(parts)
        # generic fallback
        return str(abstract_obj)
    except Exception:
        return str(abstract_obj)


def _safe_get_year(article: Dict[str, Any]) -> Optional[str]:
    try:
        # Try ArticleDate first
        dates = article.get("ArticleDate")
        if dates and isinstance(dates, list) and dates:
            y = dates[0].get("Year")
            if y:
                return str(y)
        # Then Journal PubDate
        pub = article.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
        if isinstance(pub, dict) and "Year" in pub:
            return str(pub["Year"])
        if isinstance(pub, dict) and "MedlineDate" in pub:
            # MedlineDate like "2019 Jan-Feb"
            return str(pub["MedlineDate"]).split()[0]
    except Exception:
        pass
    return None

LANG_MAP = {
    "en": "English", "eng": "English", "english": "English",
    "es": "Spanish", "spa": "Spanish", "spanish": "Spanish",
    "fr": "French", "de": "German", "zh": "Chinese",
    "pt": "Portuguese", "it": "Italian", "ru": "Russian",
    "ja": "Japanese", "ko": "Korean", "ar": "Arabic", "hi": "Hindi",
}

def build_pubmed_term(query: str, lang: Optional[str], filter_types: Optional[List[str]], mindate: Optional[int], maxdate: Optional[int]) -> str:
    term = query.strip()
    # language — map to PubMed-friendly name and use [lang]
    if lang:
        lname = LANG_MAP.get(lang.strip().lower(), lang.strip())
        term += f" AND {lname}[lang]"
    # article types
    if filter_types:
        types_clause = " OR ".join([f"{t}[Publication Type]" for t in filter_types])
        term += f" AND ({types_clause})"
    return term


def fetch_pubmed_docs(
    query: str,
    retmax: int = 50,
    mindate: Optional[int] = None,
    maxdate: Optional[int] = None,
    lang: Optional[str] = None,
    filter_types: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    try:
        from Bio import Entrez
    except ImportError:
        raise RuntimeError(
            "Biopython is required for PubMed ingestion. Install with: python3 -m pip install biopython"
        )

    email = os.getenv("PUBMED_EMAIL") or os.getenv("NCBI_EMAIL")
    if not email:
        warn("PUBMED_EMAIL not set; NCBI recommends providing a contact email.")
    Entrez.email = email or "anonymous@example.com"
    api_key = os.getenv("NCBI_API_KEY")
    if api_key:
        Entrez.api_key = api_key

    try:
        Entrez.sleep_between_tries = 1
    except Exception:
        pass

    term = build_pubmed_term(query, lang, filter_types, mindate, maxdate)
    info(f"PubMed search term: {term}")

    # 1) Search
    handle = Entrez.esearch(
        db="pubmed",
        term=term,
        retmax=retmax,
        datetype="pdat" if (mindate or maxdate) else None,
        mindate=str(mindate) if mindate else None,
        maxdate=str(maxdate) if maxdate else None,
        usehistory="n",
        retmode="xml",
    )
    record = Entrez.read(handle)
    ids = record.get("IdList", [])
    handle.close()
    time.sleep(0.35)


    if not ids:
        info("No PubMed IDs returned for this query.")
        return []

    # 2) Fetch details (XML)
    handle = Entrez.efetch(db="pubmed", id=",".join(ids), rettype="abstract", retmode="xml")
    fetched = Entrez.read(handle)
    handle.close()

    out_docs = []
    for article in fetched.get("PubmedArticle", []):
        try:
            med = article.get("MedlineCitation", {})
            pmid = str(med.get("PMID", ""))
            art = med.get("Article", {})
            title = str(art.get("ArticleTitle", "")).strip()
            abstract = _abstract_to_text(art.get("Abstract", {}).get("AbstractText"))
            if not abstract:
                # skip items with no abstract text
                continue
            journal = art.get("Journal", {}).get("Title", "")
            year = _safe_get_year(art)
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            text = f"Title: {title}\nURL: {url}\nJournal: {journal}\nYear: {year or ''}\n\n{abstract}"
            out_docs.append(
                {
                    "pmid": pmid,
                    "title": title or f"PubMed {pmid}",
                    "url": url,
                    "journal": journal,
                    "year": year,
                    "text": text,
                }
            )
        except Exception as e:
            warn(f"Failed to parse a PubMed record: {e}")
            continue

    info(f"Fetched PubMed articles: {len(out_docs)}")
    return out_docs


def ingest_text_items(items: List[Dict[str, Any]], owner_uid: Optional[str] = None) -> Dict[str, Any]:

    """
    items: list of dicts with keys:
      - 'text' (str)
      - metadata fields like 'title', 'url', 'pmid', 'journal', 'year'
    owner_uid: if provided, tag chunks so they are visible to that user only
    dry_run: when True, compute would-be counts but DO NOT persist anything
    """
    if not items:
        return {"ok": True, "added": 0, "skipped": 0}

    s = get_settings()
    embedder = get_embedder()  
    store = FaissStore(s.STORAGE_DIR, embedder.dim, provider_signature(embedder))

    # Dedup by existing PMIDs
    existing_pmids = set()
    try:
        for md in getattr(store, "_meta", []):
            if isinstance(md, dict) and md.get("pmid"):
                existing_pmids.add(str(md["pmid"]))
    except Exception:
        pass

    added = 0
    skipped = 0

    for doc in items:
        raw = doc.get("text", "")
        txt = clean_text(raw)
        if not txt:
            skipped += 1
            continue

        pmid = str(doc.get("pmid") or "")
        if pmid and pmid in existing_pmids:
            # duplicate doc — skip fully
            continue

        title = doc.get("title") or "Source"
        url = doc.get("url") or ""
        journal = doc.get("journal") or ""
        year = doc.get("year") or ""

        chunks = chunk_text(txt, chunk_size=1200, overlap=200)
        if not chunks:
            skipped += 1
            continue



        # Normal (commit) path
        embs = embedder.encode(chunks)
        metadatas = []
        for c in chunks:
            md = {
                "title": title,
                "url": url,
                "snippet": c[:240],
                "source": "pubmed" if pmid else "external",
            }
            if pmid:
                md["pmid"] = pmid
            if journal:
                md["journal"] = journal
            if year:
                md["year"] = year
            if owner_uid:
                owners = md.get("owner_uids") or []
                if owner_uid not in owners:
                    owners = [owner_uid] if not owners else owners + [owner_uid]
                md["owner_uids"] = owners
            metadatas.append(md)

        store.add(embs, metadatas)
        added += len(chunks)
        if pmid:
            existing_pmids.add(pmid)

    
    info(f"Ingested (text items): added={added}, skipped={skipped}, total={store.size()}")

    return {"ok": True, "added": added, "skipped": skipped}


# ----------------------------
# CLI entrypoint
# ----------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--path",
        action="append",
        help="File or directory to ingest. Can be specified multiple times.",
        required=False,
    )
    ap.add_argument(
        "--pubmed",
        type=str,
        help='PubMed search query, e.g. --pubmed "metformin lactic acidosis"',
        required=False,
    )
    ap.add_argument(
        "--retmax",
        type=int,
        default=int(os.getenv("PUBMED_MAX") or os.getenv("PUBMED_MAX_RESULTS", "50")),
        help="Max PubMed results"
    )
       
    ap.add_argument("--mindate", type=int, default=int(os.getenv("PUBMED_MINDATE", "0")), help="Earliest year (e.g., 2015)")
    ap.add_argument("--maxdate", type=int, default=0, help="Latest year (e.g., 2025). 0 = no max")
    ap.add_argument(
        "--lang",
        type=str,
        default=os.getenv("PUBMED_LANG", "en"),
        help="Language filter (e.g., en, es).",
    )
    ap.add_argument(
        "--types",
        type=str,
        default=os.getenv("PUBMED_FILTER_TYPES", "Guideline,Review"),
        help='Comma-separated PubMed publication types to prioritize (e.g., "Guideline,Review").',
    )

    args = ap.parse_args()

    total_added = 0
    total_skipped = 0
    ok = True

    # 1) Local paths
    if args.path:
        targets = []
        for p in args.path:
            if os.path.isdir(p):
                for root, _, files in os.walk(p):
                    for f in files:
                        targets.append(os.path.join(root, f))
            else:
                targets.append(p)
        res_local = ingest_paths(targets)
        total_added += res_local.get("added", 0)
        total_skipped += res_local.get("skipped", 0)

    # 2) PubMed query
    if args.pubmed:
        filter_types = [t.strip() for t in (args.types or "").split(",") if t.strip()]
        maxdate = args.maxdate if args.maxdate and args.maxdate > 0 else None
        mindate = args.mindate if args.mindate and args.mindate > 0 else None

        try:
            pm_docs = fetch_pubmed_docs(
                query=args.pubmed,
                retmax=args.retmax,
                mindate=mindate,
                maxdate=maxdate,
                lang=args.lang,
                filter_types=filter_types or None,
            )
            res_pm = ingest_text_items(pm_docs)
            total_added += res_pm.get("added", 0)
            total_skipped += res_pm.get("skipped", 0)
        except Exception as e:
            ok = False
            warn(f"PubMed ingestion failed: {e}")

    if not args.path and not args.pubmed:
        warn("Nothing to ingest. Provide --path and/or --pubmed.")
        ok = False

    print(json.dumps({"ok": ok, "added": total_added, "skipped": total_skipped}, indent=2))


if __name__ == "__main__":
    main()
