from __future__ import annotations

import re
from typing import Iterable

from .models import TestCertificateRecord


DATE_PATTERNS = [
    re.compile(r"(?:시험일자|검사일|Date)\s*[:\-]?\s*(\d{4}[./-]\d{1,2}[./-]\d{1,2})", re.I),
    re.compile(r"(?:시험일자|검사일|Date)\s*[:\-]?\s*(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)", re.I),
]
LOT_PATTERNS = [
    re.compile(r"(?:로트번호|Lot No\.?|Batch No\.?|LOT)\s*[:\-]?\s*([A-Za-z0-9\-_/.]+)", re.I),
]
PRODUCT_PATTERNS = [
    re.compile(r"(?:제품명|품명|시료명)\s*[:\-]?\s*(.+)", re.I),
    re.compile(r"(?:Material)\s*[:\-]?\s*(.+)", re.I),
]


def _first_match(patterns: Iterable[re.Pattern[str]], text: str) -> str:
    for pattern in patterns:
        m = pattern.search(text)
        if m:
            return m.group(1).strip()
    return ""


def extract_metadata(text: str) -> dict[str, str]:
    return {
        "issue_date": _first_match(DATE_PATTERNS, text),
        "lot_no": _first_match(LOT_PATTERNS, text),
        "product_name": _first_match(PRODUCT_PATTERNS, text),
    }


def _parse_float(raw: str) -> float | None:
    value = raw.strip().replace(",", "")
    if not value:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _parse_table_line(line: str) -> TestCertificateRecord | None:
    stripped = line.strip()
    if not stripped:
        return None

    # 1) Simple table style: a | b | c
    if "|" in stripped:
        parts = [part.strip() for part in stripped.split("|") if part.strip()]
        if len(parts) >= 3:
            item_name = parts[0]
            value = _parse_float(parts[1])
            unit = parts[2] if len(parts) > 2 else ""
            lower = _parse_float(parts[3]) if len(parts) > 3 else None
            upper = _parse_float(parts[4]) if len(parts) > 4 else None
            judgment = parts[5] if len(parts) > 5 else ""
            return TestCertificateRecord(
                item_name=item_name,
                measured_value=value,
                unit=unit,
                lower_spec=lower,
                upper_spec=upper,
                judgment=judgment,
                raw_text=line,
            )

    # 2) Loose text pattern: item value unit [lower] [upper] [judgment]
    m = re.match(
        r"^(?P<item>[^\d]+?)\s+(?P<value>-?\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z%/㎎㎍µ²]+)?"
        r"(?:\s+(?P<lower>-?\d+(?:\.\d+)?))?(?:\s+(?P<upper>-?\d+(?:\.\d+)?))?"
        r"(?:\s+(?P<judgment>PASS|FAIL|OK|NG))?$",
        stripped,
        re.I,
    )
    if not m:
        return None
    return TestCertificateRecord(
        item_name=m.group("item").strip(),
        measured_value=_parse_float(m.group("value") or ""),
        unit=(m.group("unit") or "").strip(),
        lower_spec=_parse_float(m.group("lower") or ""),
        upper_spec=_parse_float(m.group("upper") or ""),
        judgment=(m.group("judgment") or "").strip(),
        raw_text=line,
    )


def _parse_key_value_line(line: str) -> TestCertificateRecord | None:
    stripped = line.strip()
    if not stripped or ":" not in stripped:
        return None

    key, raw_value = [part.strip() for part in stripped.split(":", 1)]
    key = key.rstrip(":").strip()
    if not raw_value:
        return None

    ignored_keys = {"material", "specification", "heat no", "lot no", "condition", "test temperature"}
    if key.strip().lower() in ignored_keys:
        return None

    match = re.search(r"(-?\d+(?:\.\d+)?)\s*([A-Za-z%/°²³μµ.\-]+)?", raw_value)
    if not match:
        return None

    return TestCertificateRecord(
        item_name=key,
        measured_value=_parse_float(match.group(1) or ""),
        unit=(match.group(2) or "").strip(),
        raw_text=line,
    )


def _parse_chemistry_line(line: str) -> list[TestCertificateRecord]:
    stripped = line.strip()
    if ":" not in stripped or "chemistry" not in stripped.lower():
        return []
    _, raw_value = [part.strip() for part in stripped.split(":", 1)]
    records: list[TestCertificateRecord] = []
    for token in raw_value.split(","):
        token = token.strip().rstrip(".")
        match = re.match(r"(?P<item>[A-Za-z]+)\s+(?P<value>-?\d+(?:\.\d+)?)\s*(?P<unit>wt\.?%)?$", token, re.I)
        if not match:
            continue
        records.append(
            TestCertificateRecord(
                item_name=match.group("item").strip(),
                measured_value=_parse_float(match.group("value") or ""),
                unit=(match.group("unit") or "wt.%").strip(),
                raw_text=line,
            )
        )
    return records


def extract_records(text: str, document_name: str = "", source_page: int | None = None) -> list[TestCertificateRecord]:
    records: list[TestCertificateRecord] = []
    for line in text.splitlines():
        chemistry_records = _parse_chemistry_line(line)
        if chemistry_records:
            for rec in chemistry_records:
                rec.document_name = document_name
                rec.source_page = source_page
                records.append(rec)
            continue

        rec = _parse_table_line(line) or _parse_key_value_line(line)
        if rec is None:
            continue
        rec.document_name = document_name
        rec.source_page = source_page
        records.append(rec)
    return records
