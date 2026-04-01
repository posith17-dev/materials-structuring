from __future__ import annotations

import argparse
from pathlib import Path

from common.harness import HarnessResult, HarnessRouter, HarnessTask
from .extractor import extract_metadata, extract_records
from .normalizer import normalize_record
from .parser import extract_text_pages
from .reporter import write_outputs
from .validator import validate_records


def process_file(path: str | Path, out_dir: str | Path) -> dict[str, Path]:
    source = Path(path)
    pages = extract_text_pages(source)
    text = "\n".join(pages)
    meta = extract_metadata(text)
    records = []
    for idx, page_text in enumerate(pages, start=1):
        page_records = extract_records(page_text, document_name=source.name, source_page=idx)
        for record in page_records:
            record.issue_date = meta.get("issue_date", "")
            record.product_name = meta.get("product_name", "")
            record.lot_no = meta.get("lot_no", "")
            records.append(normalize_record(record))
    issues = validate_records(records)
    return write_outputs(out_dir, source.name, records, issues)


def _rule_task_executor(task: HarnessTask) -> HarnessResult:
    outputs = process_file(task.input_path, task.output_dir)
    return HarnessResult(
        task_type=task.task_type,
        engine="rule",
        status="ok",
        outputs={key: str(path) for key, path in outputs.items()},
        metadata={"document_type": task.document_type},
    )


def run_via_harness(path: str | Path, out_dir: str | Path) -> HarnessResult:
    router = HarnessRouter()
    router.register("rule", _rule_task_executor)
    task = HarnessTask(
        task_type="test_certificate_process",
        input_path=str(path),
        output_dir=str(out_dir),
        document_type="test_certificate",
    )
    return router.dispatch(task)


def main() -> int:
    parser = argparse.ArgumentParser(description="Rule-based test certificate MVP")
    parser.add_argument("--input", required=True, help="Input PDF/TXT/MD file")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    args = parser.parse_args()
    result = run_via_harness(args.input, args.output_dir)
    if result.status != "ok":
        for error in result.errors:
            print(f"error: {error}")
        return 1
    for key, path in result.outputs.items():
        print(f"{key}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
