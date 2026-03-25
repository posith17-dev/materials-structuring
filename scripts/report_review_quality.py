#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def _safe_pct(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return (numerator / denominator) * 100.0


def _infer_document_type_from_path(path: str) -> str:
    lower = path.lower()
    if "coa" in lower or "certificate" in lower:
        return "certificate_of_analysis"
    if "patent" in lower or "us" in lower or "wo" in lower:
        return "patent"
    return "paper"


def _load_review_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _db_counts_by_document_type(db_path: Path) -> dict[str, int]:
    import duckdb  # type: ignore

    con = duckdb.connect(str(db_path), read_only=True)
    rows = con.execute(
        """
        SELECT document_type, COUNT(*)
        FROM material_records
        GROUP BY document_type
        ORDER BY document_type
        """
    ).fetchall()
    con.close()
    return {str(doc_type): int(count) for doc_type, count in rows}


def build_report(review_paths: list[Path], raw_db: Path | None, reviewed_db: Path | None) -> dict[str, Any]:
    by_doc_type: dict[str, Counter] = defaultdict(Counter)
    by_file: list[dict[str, Any]] = []
    overall = Counter()

    for review_path in review_paths:
        payload = _load_review_payload(review_path)
        summary = payload.get("summary", {}) or {}
        source_file = str(payload.get("source_file", "")).strip()
        document_type = _infer_document_type_from_path(source_file or str(review_path))

        accepted = int(summary.get("accepted", 0))
        edited = int(summary.get("edited", 0))
        dropped = int(summary.get("dropped", 0))
        skipped = int(summary.get("skipped", 0))
        reviewed_total = accepted + edited + dropped + skipped
        kept_total = accepted + edited

        overall.update(
            {
                "accepted": accepted,
                "edited": edited,
                "dropped": dropped,
                "skipped": skipped,
                "reviewed_total": reviewed_total,
                "kept_total": kept_total,
            }
        )
        by_doc_type[document_type].update(
            {
                "accepted": accepted,
                "edited": edited,
                "dropped": dropped,
                "skipped": skipped,
                "reviewed_total": reviewed_total,
                "kept_total": kept_total,
            }
        )
        by_file.append(
            {
                "review_file": str(review_path),
                "source_file": source_file,
                "document_type": document_type,
                "accepted": accepted,
                "edited": edited,
                "dropped": dropped,
                "skipped": skipped,
                "reviewed_total": reviewed_total,
                "kept_total": kept_total,
                "accept_rate_pct": round(_safe_pct(kept_total, reviewed_total), 2),
                "drop_rate_pct": round(_safe_pct(dropped, reviewed_total), 2),
            }
        )

    doc_type_rows = []
    for document_type, counter in sorted(by_doc_type.items()):
        reviewed_total = int(counter["reviewed_total"])
        kept_total = int(counter["kept_total"])
        dropped = int(counter["dropped"])
        doc_type_rows.append(
            {
                "document_type": document_type,
                "accepted": int(counter["accepted"]),
                "edited": int(counter["edited"]),
                "dropped": dropped,
                "skipped": int(counter["skipped"]),
                "reviewed_total": reviewed_total,
                "kept_total": kept_total,
                "accept_rate_pct": round(_safe_pct(kept_total, reviewed_total), 2),
                "drop_rate_pct": round(_safe_pct(dropped, reviewed_total), 2),
            }
        )

    db_summary: dict[str, Any] = {}
    if raw_db:
        db_summary["raw_db"] = {
            "path": str(raw_db),
            "counts_by_document_type": _db_counts_by_document_type(raw_db),
        }
    if reviewed_db:
        db_summary["reviewed_db"] = {
            "path": str(reviewed_db),
            "counts_by_document_type": _db_counts_by_document_type(reviewed_db),
        }

    return {
        "overall": {
            "accepted": int(overall["accepted"]),
            "edited": int(overall["edited"]),
            "dropped": int(overall["dropped"]),
            "skipped": int(overall["skipped"]),
            "reviewed_total": int(overall["reviewed_total"]),
            "kept_total": int(overall["kept_total"]),
            "accept_rate_pct": round(_safe_pct(int(overall["kept_total"]), int(overall["reviewed_total"])), 2),
            "drop_rate_pct": round(_safe_pct(int(overall["dropped"]), int(overall["reviewed_total"])), 2),
        },
        "by_document_type": doc_type_rows,
        "by_file": by_file,
        "db_summary": db_summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviews", nargs="+", required=True, help="Reviewed decision JSON files")
    parser.add_argument("--output", required=True, help="Path to write quality report JSON")
    parser.add_argument("--raw-db", default="", help="Optional raw DuckDB path")
    parser.add_argument("--reviewed-db", default="", help="Optional reviewed DuckDB path")
    args = parser.parse_args()

    report = build_report(
        [Path(p) for p in args.reviews],
        Path(args.raw_db) if args.raw_db.strip() else None,
        Path(args.reviewed_db) if args.reviewed_db.strip() else None,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    overall = report["overall"]
    print(f"output_path={output_path}")
    print(f"reviewed_total={overall['reviewed_total']}")
    print(f"kept_total={overall['kept_total']}")
    print(f"accept_rate_pct={overall['accept_rate_pct']}")
    print(f"drop_rate_pct={overall['drop_rate_pct']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
