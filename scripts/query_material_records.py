#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    try:
        import duckdb  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("duckdb is not installed") from exc

    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, help="DuckDB file path")
    parser.add_argument("--material", default="", help="Substring filter for material/composition")
    parser.add_argument("--property", dest="property_name", default="", help="Substring filter for property")
    parser.add_argument("--document-type", default="", help="Exact filter for document type")
    parser.add_argument("--limit", type=int, default=20, help="Max rows to print")
    args = parser.parse_args()

    con = duckdb.connect(str(Path(args.db)), read_only=True)

    query = """
      SELECT document_type, document_id, material_name_or_composition, property_name,
             property_value, property_unit, test_condition, source_ref
      FROM material_records
      WHERE 1=1
    """
    params: list[str | int] = []

    if args.material.strip():
        query += " AND lower(material_name_or_composition) LIKE lower(?)"
        params.append(f"%{args.material.strip()}%")
    if args.property_name.strip():
        query += " AND lower(property_name) LIKE lower(?)"
        params.append(f"%{args.property_name.strip()}%")
    if args.document_type.strip():
        query += " AND document_type = ?"
        params.append(args.document_type.strip())

    query += " ORDER BY document_type, document_id, material_name_or_composition, property_name LIMIT ?"
    params.append(args.limit)

    rows = con.execute(query, params).fetchall()
    con.close()

    print(f"rows={len(rows)}")
    for row in rows:
        print(" | ".join("" if v is None else str(v) for v in row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
