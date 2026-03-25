#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


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
    parser.add_argument("--input", required=True, help="Path to a PDF paper")
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

    if input_path.suffix.lower() != ".pdf":
        print("input_must_be_pdf", file=sys.stderr)
        return 1

    extracted_text = extract_text_from_pdf(input_path)
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
