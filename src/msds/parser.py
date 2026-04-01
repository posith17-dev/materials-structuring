from __future__ import annotations

import re
from pathlib import Path


def _strip_html(text: str) -> str:
    text = re.sub(r"<script.*?>.*?</script>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style.*?>.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = text.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return re.sub(r"\n{2,}", "\n", text)


def extract_text(path: str | Path) -> str:
    p = Path(path)
    suffix = p.suffix.lower()

    if suffix in {".txt", ".md"}:
        return p.read_text(encoding="utf-8", errors="replace")

    if suffix in {".html", ".htm"}:
        return _strip_html(p.read_text(encoding="utf-8", errors="replace"))

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("pypdf is required to read PDF files") from exc

        reader = PdfReader(str(p))
        pages: list[str] = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return "\n".join(pages)

    raise ValueError(f"Unsupported file type: {suffix}")
