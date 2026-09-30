"""Parse job descriptions from URLs, PDFs, Word docs, or plain text."""
import io
import re
import requests
from bs4 import BeautifulSoup


def parse_url(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ResumeOptimizer/1.0)"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    return _clean(text)


def parse_pdf(file_bytes: bytes) -> str:
    # Lazy import so the module can be loaded without the cryptography chain
    from pypdf import PdfReader  # noqa: PLC0415
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = [page.extract_text() or "" for page in reader.pages]
    return _clean("\n".join(text_parts))


def parse_docx(file_bytes: bytes) -> str:
    import docx  # noqa: PLC0415
    doc = docx.Document(io.BytesIO(file_bytes))
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return _clean(text)


def parse_text(raw: str) -> str:
    return _clean(raw)


def _clean(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()
