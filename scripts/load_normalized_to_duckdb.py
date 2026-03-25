#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def main() -> int:
    try:
        import duckdb  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("duckdb is not installed") from exc

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to normalized_documents.json")
    parser.add_argument("--db", required=True, help="DuckDB file path")
    args = parser.parse_args()

    input_path = Path(args.input)
    db_path = Path(args.db)
    docs = json.loads(input_path.read_text(encoding="utf-8"))

    rows = []
    for doc in docs:
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
    con.execute("DELETE FROM material_records")
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

    print(f"db_path={db_path}")
    print(f"records={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
