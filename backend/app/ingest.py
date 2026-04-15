# app/ingest.py
import os, csv, argparse, json, time
from typing import List, Dict, Any, Tuple, Optional
import hashlib

from tenacity import retry, stop_after_attempt, wait_exponential

from .config import get_settings
from .logging_config import logger
from .utils.text import clean_text, chunk_text
from .utils.pdf import extract_pdf_text
from .rag import get_embedder, provider_signature, get_store


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
    logger.warning("Unsupported file type: %s. Skipping %s", ext, path)
    return ""


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

def ingest_paths(paths: List[str], owner_uid: Optional[str] = None) -> Dict[str, Any]:
    embedder = get_embedder()
    store = get_store()

    added = 0
    skipped = 0

    
    existing_hashes = set()
    try:
        for md in getattr(store, "_meta", []):
            owners = md.get("owner_uids") or []
            if isinstance(owners, str):
                owners = [owners]
            ch = md.get("content_hash")
            if not ch:
                continue
            if owner_uid:
                if owners and owner_uid in owners:
                    existing_hashes.add(ch)
            else:
                if not owners:   # truly global
                    existing_hashes.add(ch)
    except Exception:
        pass

    for p in paths:
        if not os.path.exists(p):
            logger.warning("Missing: %s", p)
            skipped += 1
            continue

        raw = read_file_text(p)
        txt = clean_text(raw)
        if not txt:
            skipped += 1
            continue


        chash = _content_hash(txt)
        if chash in existing_hashes:
            # already ingested for this context; skip
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
        metadatas = []
        for c in chunks:
            md = {
                "title": title,
                "url": url,
                "snippet": c[:240],
                "source_path": os.path.abspath(p),
                "source": "local",
                "content_hash": chash,
            }
            if owner_uid:
                md["owner_uids"] = [owner_uid]
            metadatas.append(md)

        store.add(embs, metadatas)
        added += len(chunks)
        existing_hashes.add(chash)

    logger.info(
        "Ingested (local): added=%d, skipped=%d, total=%d",
        added, skipped, get_store().size(),
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


def _safe_get_year(article: Dict[str, Any]) -> Optional[int]:
    try:
        # Try ArticleDate first
        dates = article.get("ArticleDate")
        if dates and isinstance(dates, list) and dates:
            y = dates[0].get("Year")
            if y:
                return int(y)
        # Then Journal PubDate
        pub = article.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
        if isinstance(pub, dict) and "Year" in pub:
            return int(pub["Year"])
        if isinstance(pub, dict) and "MedlineDate" in pub:
            # MedlineDate like "2019 Jan-Feb"
            return int(str(pub["MedlineDate"]).split()[0])
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


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def _entrez_search(term: str, retmax: int, **kwargs):
    """Retry-wrapped Entrez.esearch with guaranteed handle cleanup."""
    from Bio import Entrez
    handle = Entrez.esearch(db="pubmed", term=term, retmax=retmax, **kwargs)
    try:
        record = Entrez.read(handle)
    finally:
        handle.close()
    return record


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def _entrez_fetch(ids: List[str]):
    """Retry-wrapped Entrez.efetch with guaranteed handle cleanup."""
    from Bio import Entrez
    handle = Entrez.efetch(db="pubmed", id=",".join(ids), rettype="abstract", retmode="xml")
    try:
        fetched = Entrez.read(handle)
    finally:
        handle.close()
    return fetched


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
        logger.warning("PUBMED_EMAIL not set; NCBI recommends providing a contact email.")
    Entrez.email = email or "anonymous@example.com"
    api_key = os.getenv("NCBI_API_KEY")
    if api_key:
        Entrez.api_key = api_key

    try:
        Entrez.sleep_between_tries = 1
    except Exception:
        pass

    term = build_pubmed_term(query, lang, filter_types, mindate, maxdate)
    logger.info("PubMed search term: %s", term)

    # Rate limit: 0.11s with API key (10 req/sec), 0.35s without (3 req/sec)
    sleep_interval = 0.11 if api_key else 0.35

    # 1) Search
    record = _entrez_search(
        term=term,
        retmax=retmax,
        datetype="pdat" if (mindate or maxdate) else None,
        mindate=str(mindate) if mindate else None,
        maxdate=str(maxdate) if maxdate else None,
        usehistory="n",
        retmode="xml",
    )
    ids = record.get("IdList", [])
    time.sleep(sleep_interval)

    if not ids:
        logger.info("No PubMed IDs returned for this query.")
        return []

    # 2) Fetch details (XML)
    fetched = _entrez_fetch(ids)

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
            logger.warning("Failed to parse a PubMed record: %s", e)
            continue

    logger.info("Fetched PubMed articles: %d", len(out_docs))
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

    embedder = get_embedder()
    store = get_store()

    # - If owner_uid is provided: dedupe against PMIDs already owned by this user.
    # - If owner_uid is None (global): dedupe against PMIDs that are global (no owner_uids).
    existing_pmids_for_context = set()
    try:
        for md in getattr(store, "_meta", []):
            if not isinstance(md, dict):
                continue
            pm = md.get("pmid")
            if not pm:
                continue
            owners = md.get("owner_uids") or []
            if isinstance(owners, str):
                owners = [owners]
            if owner_uid:
                # Only consider items already owned by this user
                if owners and owner_uid in owners:
                    existing_pmids_for_context.add(str(pm))
            else:
                # Global context: only consider truly global items (no owners)
                if not owners:
                    existing_pmids_for_context.add(str(pm))
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
        # Per-context dedupe: skip only if this PMID already exists in THIS visibility context
        if pmid and pmid in existing_pmids_for_context:
            skipped += 1
            continue

        title = doc.get("title") or "Source"
        url = doc.get("url") or ""
        journal = doc.get("journal") or ""
        year = doc.get("year")

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
            # Mark this PMID as present for this context to avoid double-adding within same run
            existing_pmids_for_context.add(pmid)


    
    logger.info("Ingested (text items): added=%d, skipped=%d, total=%d", added, skipped, store.size())

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
            logger.warning("PubMed ingestion failed: %s", e)

    if not args.path and not args.pubmed:
        logger.warning("Nothing to ingest. Provide --path and/or --pubmed.")
        ok = False

    logger.info(json.dumps({"ok": ok, "added": total_added, "skipped": total_skipped}))


if __name__ == "__main__":
    main()
