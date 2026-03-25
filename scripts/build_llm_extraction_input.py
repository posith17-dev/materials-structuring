#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", required=True, help="Path to experiment JSON stub")
    parser.add_argument("--output", required=True, help="Path to write prompt bundle JSON")
    parser.add_argument("--prompt-override", default="", help="Optional prompt file path")
    args = parser.parse_args()

    experiment_path = Path(args.experiment)
    output_path = Path(args.output)

    payload = json.loads(experiment_path.read_text(encoding="utf-8"))
    prompt_path = Path(args.prompt_override.strip() or payload["prompt_file"])
    prompt_text = prompt_path.read_text(encoding="utf-8")

    bundle = {
        "source_file": payload.get("source_file", ""),
        "prompt_file": str(prompt_path),
        "instructions": prompt_text,
        "text": payload.get("text_preview", ""),
        "expected_schema": {
            "records": [
                {
                    "material_name": "",
                    "composition": "",
                    "property_name": "",
                    "property_value": "",
                    "property_unit": "",
                    "test_condition": "",
                    "source_page": "",
                    "source_excerpt": ""
                }
            ]
        }
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"output_path={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
