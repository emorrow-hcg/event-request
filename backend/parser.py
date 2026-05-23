"""Parse job descriptions from URLs, PDFs, Word docs, or plain text."""
import io
import re
import requests
import pdfplumber
import docx
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
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    return _clean("\n".join(text_parts))


def parse_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return _clean(text)


def parse_text(raw: str) -> str:
    return _clean(raw)


def _clean(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()
