from __future__ import annotations

from .models import TestCertificateRecord


FIELD_ALIASES = {
    "시험일자": "issue_date",
    "검사일": "issue_date",
    "date": "issue_date",
    "제품명": "product_name",
    "품명": "product_name",
    "시료명": "product_name",
    "로트번호": "lot_no",
    "lot": "lot_no",
    "batch no.": "lot_no",
    "항목": "item_name",
    "시험항목": "item_name",
    "item": "item_name",
    "측정값": "measured_value",
    "결과": "measured_value",
    "value": "measured_value",
    "규격하한": "lower_spec",
    "하한": "lower_spec",
    "lsl": "lower_spec",
    "규격상한": "upper_spec",
    "상한": "upper_spec",
    "usl": "upper_spec",
    "판정": "judgment",
    "결과판정": "judgment",
}

UNIT_ALIASES = {
    "mpa": "MPa",
    "n/mm2": "MPa",
    "n/mm^2": "MPa",
    "wt%": "%",
    "%": "%",
    "ppm": "ppm",
    "mg/l": "mg/L",
}


def normalize_field_name(name: str) -> str:
    return FIELD_ALIASES.get(name.strip().lower(), name.strip())


def normalize_unit(unit: str) -> str:
    return UNIT_ALIASES.get(unit.strip().lower(), unit.strip())


def normalize_record(record: TestCertificateRecord) -> TestCertificateRecord:
    record.unit = normalize_unit(record.unit)
    if record.item_name:
        record.item_name = record.item_name.strip()
    if record.judgment:
        record.judgment = record.judgment.strip().upper()
    return record
