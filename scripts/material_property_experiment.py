#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from html.parser import HTMLParser


PROMPT_PATH = Path("/home/ubuntu/materials-structuring/prompts/material_property_extraction_prompt.md")


def extract_text_from_pdf(pdf_path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "pypdf is not installed. Install it before running the PDF experiment."
        ) from exc

    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for idx, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if not text:
            continue
        pages.append(f"[PAGE {idx}]\n{text}")
    return "\n\n".join(pages)


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag in {"p", "div", "section", "article", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "caption"}:
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag in {"p", "div", "section", "article", "li", "tr", "caption"}:
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = data.strip()
        if text:
            self._chunks.append(text)

    def get_text(self) -> str:
        text = " ".join(self._chunks)
        text = re.sub(r"\n\s*\n+", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()


def extract_text_from_html(html_path: Path) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(html_path.read_text(encoding="utf-8", errors="ignore"))
    return parser.get_text()


def build_output_stub(source_path: Path, extracted_text: str) -> dict:
    preview = extracted_text[:3000]
    return {
        "source_file": str(source_path),
        "prompt_file": str(PROMPT_PATH),
        "status": "ready_for_llm_extraction",
        "records": [],
        "text_preview": preview,
        "notes": [
            "Run an LLM extraction using the prompt file and the extracted text.",
            "Keep only explicit material-property records.",
            "Save validated records back into this JSON structure.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to a PDF or HTML paper")
    parser.add_argument(
        "--output",
        default="/home/ubuntu/materials-structuring/outputs/material_property_experiment.json",
        help="Path to write the JSON stub",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"input_not_found={input_path}", file=sys.stderr)
        return 1

    suffix = input_path.suffix.lower()
    if suffix == ".pdf":
        extracted_text = extract_text_from_pdf(input_path)
    elif suffix in {".html", ".htm"}:
        extracted_text = extract_text_from_html(input_path)
    else:
        print("input_must_be_pdf_or_html", file=sys.stderr)
        return 1
    if not extracted_text.strip():
        print("no_text_extracted", file=sys.stderr)
        return 1

    payload = build_output_stub(input_path, extracted_text)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"output_path={output_path}")
    print(f"chars_extracted={len(extracted_text)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
