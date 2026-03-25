#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _collect_reviewed_records(review_payload: dict) -> list[dict]:
    reviewed = review_payload.get("reviewed_records")
    if not isinstance(reviewed, list):
        return []

    accepted_records: list[dict] = []
    for item in reviewed:
        if not isinstance(item, dict):
            continue
        decision = str(item.get("decision", "")).strip().lower()
        if decision == "accept" and isinstance(item.get("record"), dict):
            accepted_records.append(item["record"])
        elif decision == "edit" and isinstance(item.get("record"), dict):
            accepted_records.append(item["record"])
    return accepted_records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", required=True, help="Original experiment JSON path")
    parser.add_argument("--review", required=True, help="Reviewed decisions JSON path")
    parser.add_argument("--output", required=True, help="Merged reviewed JSON output path")
    args = parser.parse_args()

    experiment_path = Path(args.experiment)
    review_path = Path(args.review)
    output_path = Path(args.output)

    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    review_payload = json.loads(review_path.read_text(encoding="utf-8"))
    reviewed_records = _collect_reviewed_records(review_payload)

    merged = dict(experiment)
    merged["status"] = "review_completed"
    merged["records"] = reviewed_records
    merged["review_file"] = str(review_path)
    merged["review_summary"] = review_payload.get("summary", {})

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"output_path={output_path}")
    print(f"records={len(reviewed_records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
