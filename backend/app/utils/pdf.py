from pypdf import PdfReader
def extract_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    texts = []
    for page in reader.pages:
        try: texts.append(page.extract_text() or '')
        except Exception: pass
    return "\n".join(texts)
