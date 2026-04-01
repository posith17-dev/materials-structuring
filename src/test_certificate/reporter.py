from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from .models import TestCertificateRecord, ValidationIssue


def build_report(
    source_file: str,
    records: list[TestCertificateRecord],
    issues: list[ValidationIssue],
) -> str:
    total = len(records)
    issue_count = len(issues)
    pass_count = sum(1 for r in records if r.judgment == "PASS")
    fail_count = sum(1 for r in records if r.judgment == "FAIL")

    lines = [
        "# 시험성적서 규칙 기반 MVP 리포트",
        "",
        f"- source_file: `{source_file}`",
        f"- records: `{total}`",
        f"- issues: `{issue_count}`",
        f"- pass: `{pass_count}`",
        f"- fail: `{fail_count}`",
        "",
        "## Issues",
    ]
    if issues:
        for issue in issues:
            lines.append(
                f"- `{issue.rule}` [{issue.severity}] {issue.message}"
                + (f" / item={issue.item_name}" if issue.item_name else "")
            )
    else:
        lines.append("- none")

    lines += ["", "## Records"]
    for record in records:
        lines.append(
            f"- {record.item_name or 'N/A'} | {record.measured_value} {record.unit} | "
            f"spec={record.lower_spec}~{record.upper_spec} | {record.judgment}"
        )

    return "\n".join(lines)


def write_outputs(
    out_dir: str | Path,
    source_file: str,
    records: list[TestCertificateRecord],
    issues: list[ValidationIssue],
) -> dict[str, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    json_path = out / "result.json"
    csv_path = out / "result.csv"
    md_path = out / "report.md"

    payload = {
        "source_file": source_file,
        "records": [asdict(r) for r in records],
        "issues": [asdict(i) for i in issues],
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "document_name",
                "issue_date",
                "product_name",
                "lot_no",
                "item_name",
                "measured_value",
                "unit",
                "lower_spec",
                "upper_spec",
                "judgment",
                "source_page",
                "raw_text",
                "source_ref",
            ],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))

    md_path.write_text(build_report(source_file, records, issues), encoding="utf-8")

    return {"json": json_path, "csv": csv_path, "md": md_path}
