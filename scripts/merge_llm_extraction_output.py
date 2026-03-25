#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", required=True, help="Original experiment JSON path")
    parser.add_argument("--llm-output", required=True, help="LLM JSON output path")
    parser.add_argument("--output", required=True, help="Merged JSON output path")
    args = parser.parse_args()

    experiment = json.loads(Path(args.experiment).read_text(encoding="utf-8"))
    llm_output = json.loads(Path(args.llm_output).read_text(encoding="utf-8"))

    merged = dict(experiment)
    merged["status"] = "llm_extraction_completed"
    merged["records"] = llm_output.get("records", [])

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"output_path={output_path}")
    print(f"records={len(merged['records'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
