#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from normalize_material_records import normalize_payload


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_duckdb() -> object:
    try:
        import duckdb  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("duckdb is not installed") from exc
    return duckdb


def _load_to_duckdb(db_path: Path, normalized_docs: list[dict]) -> int:
    duckdb = _load_duckdb()
    rows = []
    for doc in normalized_docs:
        for rec in doc.get("records", []):
            rows.append(
                (
                    rec.get("document_id", ""),
                    rec.get("document_type", ""),
                    rec.get("document_title", ""),
                    rec.get("source_file", ""),
                    rec.get("material_name_or_composition", ""),
                    rec.get("property_name", ""),
                    rec.get("canonical_property_name", ""),
                    rec.get("property_value", ""),
                    rec.get("property_unit", ""),
                    rec.get("canonical_property_unit", ""),
                    rec.get("test_condition", ""),
                    rec.get("source_ref", ""),
                )
            )

    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    con.execute("DROP TABLE IF EXISTS material_records")
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS material_records (
          document_id VARCHAR,
          document_type VARCHAR,
          document_title VARCHAR,
          source_file VARCHAR,
          material_name_or_composition VARCHAR,
          property_name VARCHAR,
          canonical_property_name VARCHAR,
          property_value VARCHAR,
          property_unit VARCHAR,
          canonical_property_unit VARCHAR,
          test_condition VARCHAR,
          source_ref VARCHAR
        )
        """
    )
    con.executemany(
        """
        INSERT INTO material_records (
          document_id, document_type, document_title, source_file,
          material_name_or_composition, property_name, canonical_property_name,
          property_value, property_unit, canonical_property_unit,
          test_condition, source_ref
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    count = con.execute("SELECT COUNT(*) FROM material_records").fetchone()[0]
    con.close()
    return int(count)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", nargs="+", required=True, help="Reviewed experiment JSON files")
    parser.add_argument("--normalized-output", required=True, help="Path to normalized JSON output")
    parser.add_argument("--jsonl-output", default="", help="Optional normalized JSONL output")
    parser.add_argument("--db", default="", help="Optional DuckDB file path")
    args = parser.parse_args()

    normalized_docs: list[dict] = []
    jsonl_rows: list[dict] = []

    for path_str in args.input:
        path = Path(path_str)
        payload = json.loads(path.read_text(encoding="utf-8"))
        normalized = normalize_payload(payload)
        normalized_docs.append(normalized)
        jsonl_rows.extend(normalized["records"])

    normalized_output = Path(args.normalized_output)
    _write_json(normalized_output, normalized_docs)
    print(f"normalized_output={normalized_output}")
    print(f"documents={len(normalized_docs)}")
    print(f"records={len(jsonl_rows)}")

    if args.jsonl_output:
        jsonl_output = Path(args.jsonl_output)
        jsonl_output.parent.mkdir(parents=True, exist_ok=True)
        jsonl_output.write_text(
            "\n".join(json.dumps(row, ensure_ascii=False) for row in jsonl_rows) + "\n",
            encoding="utf-8",
        )
        print(f"jsonl_output={jsonl_output}")

    if args.db:
        db_count = _load_to_duckdb(Path(args.db), normalized_docs)
        print(f"db_path={args.db}")
        print(f"db_records={db_count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
