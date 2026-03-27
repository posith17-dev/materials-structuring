#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from material_property_experiment import extract_text
from msds_rule_validate import parse_msds_records


SUPPORTED_SUFFIXES = {".html", ".htm", ".pdf"}


def _iter_inputs(input_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(input_dir.iterdir()):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            files.append(path)
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, help="Directory with MSDS HTML/PDF files")
    parser.add_argument("--output-dir", required=True, help="Directory for outputs")
    parser.add_argument("--limit", type=int, default=10, help="Maximum files to process")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    inputs = _iter_inputs(input_dir)[: args.limit]
    if not inputs:
        raise SystemExit(f"no supported files in {input_dir}")

    summary: list[dict[str, object]] = []
    total_records = 0
    for idx, path in enumerate(inputs, start=1):
        text = extract_text(path)
        records = parse_msds_records(text)
        total_records += len(records)

        payload = {
            "source_file": str(path),
            "document_type": "msds",
            "status": "rule_extraction_completed",
            "records": records,
            "record_count": len(records),
        }

        stem = path.stem
        out_path = output_dir / f"{stem}_rule_output.json"
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        summary.append(
            {
                "source_file": str(path),
                "output_file": str(out_path),
                "record_count": len(records),
            }
        )
        print(f"[{idx}/{len(inputs)}] {path.name}: records={len(records)}")

    report_lines = []
    report_lines.append("# MSDS Batch Validation Report")
    report_lines.append("")
    report_lines.append(f"- **Input dir**: {input_dir}")
    report_lines.append(f"- **Files processed**: {len(inputs)}")
    report_lines.append(f"- **Total records**: {total_records}")
    report_lines.append("")
    report_lines.append("## Files")
    report_lines.append("")
    report_lines.append("| source_file | record_count | output_file |")
    report_lines.append("|---|---:|---|")
    for item in summary:
        report_lines.append(
            f"| {item['source_file']} | {item['record_count']} | {item['output_file']} |"
        )

    report_path = output_dir / "msds_batch_validation_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    manifest = {
        "input_dir": str(input_dir),
        "files_processed": len(inputs),
        "total_records": total_records,
        "files": summary,
    }
    manifest_path = output_dir / "msds_batch_validation_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"report={report_path}")
    print(f"manifest={manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
