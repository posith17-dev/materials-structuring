from __future__ import annotations

from pathlib import Path
import re


def _strip_html(text: str) -> str:
    text = re.sub(r"<script.*?>.*?</script>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style.*?>.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = text.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def extract_text_pages(path: str | Path) -> list[str]:
    """Return a list of page-like text chunks.

    Supported inputs:
    - .txt / .md: treated as a single page
    - .pdf: tries pypdf first, falls back to a single empty page if unavailable
    """

    p = Path(path)
    suffix = p.suffix.lower()

    if suffix in {".txt", ".md"}:
        return [p.read_text(encoding="utf-8", errors="replace")]

    if suffix in {".html", ".htm"}:
        return [_strip_html(p.read_text(encoding="utf-8", errors="replace"))]

    if suffix == ".pdf":
        head = p.read_text(encoding="utf-8", errors="ignore")[:500].lstrip()
        if head.lower().startswith("<html") or head.lower().startswith("<!doctype html"):
            return [_strip_html(p.read_text(encoding="utf-8", errors="replace"))]
        try:
            from pypdf import PdfReader  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("pypdf is required to read PDF files") from exc

        reader = PdfReader(str(p))
        pages: list[str] = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return pages or [""]

    raise ValueError(f"Unsupported file type: {suffix}")


def extract_text(path: str | Path) -> str:
    return "\n".join(extract_text_pages(path))
