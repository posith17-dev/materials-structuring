#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


RECORD_FIELDS = [
    "material_name",
    "composition",
    "property_name",
    "property_value",
    "property_unit",
    "test_condition",
    "source_page",
    "source_excerpt",
]


def _load_records(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("records")
    if not isinstance(records, list):
        raise ValueError("input must contain a top-level records list")
    return [record for record in records if isinstance(record, dict)]


def _prompt_edit(record: dict) -> dict:
    edited = dict(record)
    print("edit mode: 엔터를 누르면 기존 값을 유지합니다.")
    for field in RECORD_FIELDS:
        current = "" if edited.get(field) is None else str(edited.get(field, ""))
        new_value = input(f"{field} [{current}]: ").strip()
        if new_value:
            edited[field] = new_value
    return edited


def _print_record(index: int, record: dict) -> None:
    print(f"\n=== record {index} ===")
    for field in RECORD_FIELDS:
        value = "" if record.get(field) is None else str(record.get(field, ""))
        print(f"{field}: {value}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to LLM output JSON with records[]")
    parser.add_argument("--output", required=True, help="Path to write review decisions JSON")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    records = _load_records(input_path)

    review_payload = {
        "source_file": str(input_path),
        "reviewed_records": [],
        "summary": {
            "accepted": 0,
            "edited": 0,
            "dropped": 0,
            "skipped": 0,
        },
    }

    print(f"records={len(records)}")
    print("명령: [a]ccept / [e]dit / [d]rop / [s]kip / [q]uit")

    for idx, record in enumerate(records, start=1):
        _print_record(idx, record)
        while True:
            action = input("action [a/e/d/s/q]: ").strip().lower() or "a"
            if action not in {"a", "e", "d", "s", "q"}:
                print("잘못된 입력입니다. a/e/d/s/q 중 하나를 입력하세요.")
                continue
            break

        if action == "q":
            break
        if action == "a":
            review_payload["reviewed_records"].append({"decision": "accept", "record": record})
            review_payload["summary"]["accepted"] += 1
        elif action == "e":
            edited = _prompt_edit(record)
            review_payload["reviewed_records"].append(
                {"decision": "edit", "original_record": record, "record": edited}
            )
            review_payload["summary"]["edited"] += 1
        elif action == "d":
            review_payload["reviewed_records"].append({"decision": "drop", "record": record})
            review_payload["summary"]["dropped"] += 1
        elif action == "s":
            review_payload["reviewed_records"].append({"decision": "skip", "record": record})
            review_payload["summary"]["skipped"] += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(review_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"output_path={output_path}")
    print(json.dumps(review_payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
