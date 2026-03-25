#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from html.parser import HTMLParser


PROMPT_PATH = Path("/home/ubuntu/materials-structuring/prompts/material_property_extraction_prompt.md")
PROPERTY_KEYWORDS = [
    "tensile strength",
    "ultimate tensile strength",
    "yield strength",
    "ductility",
    "elongation",
    "young",
    "modulus",
    "hardness",
    "grain size",
    "density",
    "transition temperature",
    "penetration depth",
    "heat capacity",
    "resistance",
    "조성",
    "인장강도",
    "항복강도",
    "연신율",
    "탄성계수",
    "경도",
    "밀도",
]
UNIT_PATTERNS = [
    "MPa",
    "GPa",
    "ksi",
    "psi",
    "wt%",
    "at.%",
    "%",
    "K",
    "GHz",
    "µm",
    "um",
    "mm",
    "m^-1",
    "HRC",
]
NOISE_PATTERNS = [
    r"Skip to main content",
    r"An official website of the United States government",
    r"Official websites use \.gov.*?official, secure websites\.",
    r"Search PMC Full-Text Archive Search in PMC",
    r"Journal List",
    r"User Guide",
    r"Dashboard",
    r"Publications",
    r"Account settings",
    r"Log out",
    r"Log in",
    r"Search NCBI",
    r"Search in PubMed",
    r"Search in PMC",
    r"View in NLM Catalog",
    r"Add to search",
    r"As a library, NLM provides access to scientific literature\..*?Copyright Notice",
    r"Find articles by .*?(?=\n|$)",
]


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


def extract_text(input_path: Path) -> str:
    suffix = input_path.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(input_path)
    if suffix in {".html", ".htm"}:
        return extract_text_from_html(input_path)
    raise ValueError("input_must_be_pdf_or_html")


def clean_common_noise(extracted_text: str) -> str:
    lines = extracted_text.splitlines()
    cleaned_lines: list[str] = []
    for line in lines:
        text = line.strip()
        if not text:
            cleaned_lines.append("")
            continue
        for pattern in NOISE_PATTERNS:
            text = re.sub(pattern, " ", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            cleaned_lines.append(text)
        else:
            cleaned_lines.append("")

    text = "\n".join(cleaned_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _score_segment(text: str) -> tuple[int, dict[str, object]]:
    lower = text.lower()
    score = 0
    flags: list[str] = []
    matched_units: list[str] = []
    matched_keywords: list[str] = []
    if re.search(r"\d", text):
        score += 1
        flags.append("has_number")
    for unit in UNIT_PATTERNS:
        if unit.lower() in lower:
            score += 2
            matched_units.append(unit)
    for keyword in PROPERTY_KEYWORDS:
        if keyword in lower:
            score += 3
            matched_keywords.append(keyword)
    if "figure" in lower or "table" in lower:
        score += 1
        flags.append("has_figure_or_table_ref")
    if "±" in text or re.search(r"\d+\s*[–-]\s*\d+", text):
        score += 2
        flags.append("has_range_or_error")
    return score, {
        "flags": flags,
        "matched_units": sorted(set(matched_units)),
        "matched_keywords": sorted(set(matched_keywords)),
    }


def select_candidate_segments(extracted_text: str, max_segments: int = 12) -> list[dict[str, object]]:
    raw_segments = re.split(r"\n\s*\n+", extracted_text)
    cleaned_segments: list[str] = []
    for segment in raw_segments:
        normalized = re.sub(r"\s+", " ", segment).strip()
        if len(normalized) < 40:
            continue
        cleaned_segments.append(normalized)

    if len(cleaned_segments) <= 2:
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-ZΑ-Ω가-힣])", extracted_text)
        cleaned_segments = []
        window_size = 3
        for idx in range(len(sentences)):
            chunk = " ".join(s.strip() for s in sentences[idx : idx + window_size] if s.strip())
            chunk = re.sub(r"\s+", " ", chunk).strip()
            if len(chunk) >= 80:
                cleaned_segments.append(chunk)

    scored: list[tuple[int, int, str, dict[str, object]]] = []
    for segment in cleaned_segments:
        score, match_info = _score_segment(segment)
        if score >= 4:
            scored.append((score, len(segment), segment, match_info))

    scored.sort(key=lambda item: (-item[0], -item[1], item[2]))

    selected: list[dict[str, object]] = []
    seen = set()
    for score, _, segment, match_info in scored:
        if segment in seen:
            continue
        seen.add(segment)
        selected.append(
            {
                "score": score,
                "flags": match_info["flags"],
                "matched_units": match_info["matched_units"],
                "matched_keywords": match_info["matched_keywords"],
                "text": segment,
            }
        )
        if len(selected) >= max_segments:
            break
    return selected


def build_output_stub(source_path: Path, extracted_text: str) -> dict:
    cleaned_text = clean_common_noise(extracted_text)
    preview = cleaned_text[:3000]
    candidate_segment_details = select_candidate_segments(cleaned_text)
    candidate_segments = [str(item["text"]) for item in candidate_segment_details]
    candidate_text = "\n\n".join(candidate_segments)
    return {
        "source_file": str(source_path),
        "prompt_file": str(PROMPT_PATH),
        "status": "ready_for_llm_extraction",
        "records": [],
        "text_preview": preview,
        "cleaned_text_preview": cleaned_text[:6000],
        "candidate_segment_details": candidate_segment_details,
        "candidate_segments": candidate_segments,
        "candidate_text": candidate_text,
        "notes": [
            "Run an LLM extraction using the prompt file and the extracted text.",
            "Prefer candidate_text or candidate_segments before using the full document preview.",
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

    try:
        extracted_text = extract_text(input_path)
    except ValueError:
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
