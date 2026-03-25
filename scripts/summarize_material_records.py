#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import shutil
import tempfile


def _open_readonly_copy(db_path: Path):
    import duckdb  # type: ignore

    tmp_dir = Path(tempfile.mkdtemp(prefix="materials-duckdb-summary-"))
    tmp_db = tmp_dir / db_path.name
    shutil.copy2(db_path, tmp_db)
    return duckdb.connect(str(tmp_db), read_only=True)


def main() -> int:
    try:
        import duckdb  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("duckdb is not installed") from exc

    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, help="DuckDB file path")
    parser.add_argument("--material", required=True, help="Substring filter for material/composition")
    parser.add_argument("--limit", type=int, default=20, help="Max grouped rows to print")
    args = parser.parse_args()

    con = _open_readonly_copy(Path(args.db))
    rows = con.execute(
        """
        SELECT
          canonical_property_name,
          property_name,
          property_value,
          property_unit,
          document_type
        FROM material_records
        WHERE lower(material_name_or_composition) LIKE lower(?)
        ORDER BY canonical_property_name, property_name, property_value
        """,
        [f"%{args.material.strip()}%"],
    ).fetchall()
    con.close()

    grouped: dict[str, dict[str, object]] = defaultdict(
        lambda: {"display_name": "", "count": 0, "values": set(), "document_types": set()}
    )

    for canonical_name, property_name, property_value, property_unit, document_type in rows:
        key = str(canonical_name or "").strip() or str(property_name or "").strip()
        group = grouped[key]
        if not group["display_name"] and property_name:
            group["display_name"] = str(property_name)
        group["count"] = int(group["count"]) + 1
        value_display = str(property_value or "").strip()
        unit_display = str(property_unit or "").strip()
        if unit_display:
            value_display = f"{value_display} {unit_display}".strip()
        if value_display:
            group["values"].add(value_display)
        if document_type:
            group["document_types"].add(str(document_type))

    items = sorted(grouped.items(), key=lambda item: item[0])[: args.limit]
    print(f"rows={len(items)}")
    for canonical_name, group in items:
        display_name = str(group["display_name"] or canonical_name)
        count = str(group["count"])
        values_seen = "; ".join(sorted(group["values"])) if group["values"] else ""
        document_types = ", ".join(sorted(group["document_types"])) if group["document_types"] else ""
        print(" | ".join([canonical_name, display_name, count, values_seen, document_types]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
