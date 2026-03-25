#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REQUIRED_KEYS = {
    "material_name",
    "composition",
    "property_name",
    "property_value",
    "property_unit",
    "test_condition",
    "source_page",
    "source_excerpt",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to LLM JSON output")
    args = parser.parse_args()

    input_path = Path(args.input)
    payload = json.loads(input_path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        print("invalid_root_type", file=sys.stderr)
        return 1

    records = payload.get("records")
    if not isinstance(records, list):
        print("missing_or_invalid_records", file=sys.stderr)
        return 1

    for idx, record in enumerate(records):
        if not isinstance(record, dict):
            print(f"record_{idx}_not_object", file=sys.stderr)
            return 1
        missing = REQUIRED_KEYS - set(record.keys())
        if missing:
            missing_list = ",".join(sorted(missing))
            print(f"record_{idx}_missing_keys={missing_list}", file=sys.stderr)
            return 1

    print(f"records={len(records)}")
    print("validation=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
