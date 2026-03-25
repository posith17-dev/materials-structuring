#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PROPERTY_ALIASES = {
    "인장강도": "ultimate_tensile_strength",
    "인장강도(uts)": "ultimate_tensile_strength",
    "평균 인장강도(uts)": "ultimate_tensile_strength",
    "uts": "ultimate_tensile_strength",
    "ultimate tensile strength": "ultimate_tensile_strength",
    "yield strength": "yield_strength",
    "yield strength (0.2% offset)": "yield_strength",
    "0.2% yield strength": "yield_strength",
    "항복강도": "yield_strength",
    "항복강도(0.2% offset)": "yield_strength",
    "평균 항복강도(0.2% offset)": "yield_strength",
    "elongation": "elongation",
    "elongation to failure": "elongation",
    "연신율": "elongation",
    "young's modulus": "youngs_modulus",
    "elastic modulus": "youngs_modulus",
    "탄성계수": "youngs_modulus",
    "경도": "hardness",
    "hardness": "hardness",
    "초전도 전이온도": "critical_temperature",
    "transition temperature": "critical_temperature",
    "superconducting transition temperature": "critical_temperature",
    "초전도 전이온도(tc, fit)": "critical_temperature",
    "london penetration depth": "london_penetration_depth",
    "공진 주파수": "resonant_frequency",
    "kinetic inductance fraction, αki": "kinetic_inductance_fraction",
    "내부 품질계수, qi": "internal_quality_factor",
    "magnetic participation ratio": "magnetic_participation_ratio",
    "조성(ti)": "composition_ti",
    "조성(al)": "composition_al",
    "조성(v)": "composition_v",
    "조성(fe 불순물)": "composition_fe",
    "조성(fe)": "composition_fe",
    "조성(o)": "composition_o",
    "밀도": "density",
    "density": "density",
    "전단강도": "shear_strength",
    "shear strength": "shear_strength",
}

UNIT_ALIASES = {
    "mpa": "MPa",
    "gpa": "GPa",
    "ksi": "ksi",
    "psi": "psi",
    "wt%": "wt%",
    "k": "K",
    "ghz": "GHz",
    "µm": "µm",
    "um": "µm",
    "m^-1": "m^-1",
    "%": "%",
    "hrc": "HRC",
}


def _infer_document_type(payload: dict[str, Any]) -> str:
    explicit = str(payload.get("document_type", "")).strip()
    if explicit:
        return explicit
    source_file = str(payload.get("source_file", "")).lower()
    title = _infer_document_title(payload).lower()
    if "coa" in source_file or "certificate" in source_file or "coa" in title or "certificate" in title:
        return "certificate_of_analysis"
    if payload.get("patent_number"):
        return "patent"
    if "patent" in source_file or "patent" in title:
        return "patent"
    return "paper"


def _infer_document_title(payload: dict[str, Any]) -> str:
    for key in ("document_title", "article_title", "paper_title", "title"):
        value = str(payload.get(key, "")).strip()
        if value:
            return value
    return ""


def _infer_document_id(payload: dict[str, Any], source_file: str) -> str:
    patent = str(payload.get("patent_number", "")).strip()
    if patent:
        return patent
    title = _infer_document_title(payload)
    if "PMC" in title:
        for token in title.replace("-", " ").split():
            if token.startswith("PMC"):
                return token
    stem = Path(source_file).stem
    if stem:
        if stem.lower().endswith("_material_properties"):
            stem = stem[: -len("_material_properties")]
        return f"doc:{stem}"
    return "doc:unknown"


def _iter_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    records = payload.get("records")
    if isinstance(records, list):
        return [r for r in records if isinstance(r, dict)]
    records = payload.get("material_records")
    if isinstance(records, list):
        return [r for r in records if isinstance(r, dict)]
    return []


def _canonicalize_property_name(value: str) -> str:
    key = value.strip().lower()
    if not key:
        return ""
    return PROPERTY_ALIASES.get(key, key.replace(" ", "_").replace("-", "_"))


def _canonicalize_unit(value: str) -> str:
    key = value.strip()
    if not key:
        return ""
    return UNIT_ALIASES.get(key.lower(), key)


def _material_name_or_composition(record: dict[str, Any]) -> str:
    direct = str(record.get("material_name_or_composition", "")).strip()
    if direct:
        return direct
    material_name = str(record.get("material_name", "")).strip()
    composition = str(record.get("composition", "")).strip()
    if material_name and composition:
        return f"{material_name} ({composition})"
    return material_name or composition


def normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    source_file = str(payload.get("source_file", "")).strip()
    document_type = _infer_document_type(payload)
    document_title = _infer_document_title(payload)
    document_id = _infer_document_id(payload, source_file)

    normalized_records: list[dict[str, Any]] = []
    for record in _iter_records(payload):
        property_name = str(record.get("property", record.get("property_name", ""))).strip()
        property_unit = str(record.get("unit", record.get("property_unit", ""))).strip()
        normalized_records.append(
            {
                "material_name_or_composition": _material_name_or_composition(record),
                "property_name": property_name,
                "canonical_property_name": _canonicalize_property_name(property_name),
                "property_value": str(record.get("value", record.get("property_value", ""))).strip(),
                "property_unit": property_unit,
                "canonical_property_unit": _canonicalize_unit(property_unit),
                "test_condition": str(
                    record.get("experimental_condition", record.get("test_condition", ""))
                ).strip(),
                "source_ref": str(record.get("source", record.get("source_page", ""))).strip(),
                "source_file": source_file,
                "document_type": document_type,
                "document_title": document_title,
                "document_id": document_id,
            }
        )

    return {
        "source_file": source_file,
        "document_type": document_type,
        "document_title": document_title,
        "document_id": document_id,
        "records": normalized_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", nargs="+", required=True, help="Input JSON files")
    parser.add_argument("--output", required=True, help="Output normalized JSON file")
    parser.add_argument("--jsonl-output", default="", help="Optional normalized JSONL output")
    args = parser.parse_args()

    normalized_docs = []
    jsonl_rows = []

    for path_str in args.input:
        path = Path(path_str)
        payload = json.loads(path.read_text(encoding="utf-8"))
        normalized = normalize_payload(payload)
        normalized_docs.append(normalized)
        jsonl_rows.extend(normalized["records"])

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(normalized_docs, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.jsonl_output:
        jsonl_path = Path(args.jsonl_output)
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        jsonl_path.write_text(
            "\n".join(json.dumps(row, ensure_ascii=False) for row in jsonl_rows) + "\n",
            encoding="utf-8",
        )

    print(f"documents={len(normalized_docs)}")
    print(f"records={len(jsonl_rows)}")
    print(f"output_path={output_path}")
    if args.jsonl_output:
        print(f"jsonl_output_path={args.jsonl_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
