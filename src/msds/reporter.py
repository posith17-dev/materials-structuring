from __future__ import annotations

import csv
import json
from pathlib import Path


def write_outputs(out_dir: str | Path, source_file: str, records: list[dict[str, str]]) -> dict[str, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    json_path = out / "result.json"
    csv_path = out / "result.csv"
    md_path = out / "report.md"

    payload = {
        "source_file": source_file,
        "document_type": "msds",
        "status": "rule_extraction_completed",
        "records": records,
        "record_count": len(records),
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "material_name",
                "composition",
                "property_name",
                "property_value",
                "property_unit",
                "test_condition",
                "source_page",
                "source_excerpt",
            ],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(record)

    lines = [
        "# MSDS Rule Validation Report",
        "",
        f"- source_file: `{source_file}`",
        f"- records: `{len(records)}`",
        "",
        "## Extracted Records",
        "",
        "| material_name | composition | property_name | value | unit | condition |",
        "|---|---|---|---|---|---|",
    ]
    for rec in records:
        lines.append(
            "| "
            + " | ".join(
                [
                    rec["material_name"],
                    rec["composition"],
                    rec["property_name"],
                    rec["property_value"],
                    rec["property_unit"],
                    rec["test_condition"],
                ]
            )
            + " |"
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {"json": json_path, "csv": csv_path, "md": md_path}
