from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    src_root = project_root / "src"
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from common.harness.cli import build_router
    from common.harness.schemas import HarnessTask

    parser = argparse.ArgumentParser(description="Run a direct harness task")
    parser.add_argument("--task-type", required=True, help="Task type such as summarize or deep_review")
    parser.add_argument("--document-type", default="generic", help="Logical document type")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--input", default="", help="Optional input file path")
    parser.add_argument("--prompt", default="", help="Direct prompt text")
    parser.add_argument("--prompt-file", default="", help="Optional prompt file path")
    parser.add_argument(
        "--provider",
        default="",
        choices=["", "openai", "anthropic", "gemini"],
        help="Optional provider override",
    )
    parser.add_argument(
        "--providers",
        default="",
        help="Optional comma-separated provider chain, e.g. openai,anthropic,gemini",
    )
    parser.add_argument("--model", default="", help="Optional model override")
    parser.add_argument(
        "--labels",
        default="",
        help="Optional comma-separated labels for classify tasks, e.g. coa,msds",
    )
    parser.add_argument("--expected-output", default="", help="Human-readable output expectation")
    parser.add_argument("--json-schema-file", default="", help="Optional JSON schema file")
    args = parser.parse_args()

    prompt = args.prompt
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8")

    metadata: dict[str, object] = {}
    if prompt:
        metadata["prompt"] = prompt
    if args.providers.strip():
        metadata["providers"] = [provider.strip() for provider in args.providers.split(",") if provider.strip()]
    if args.provider:
        metadata["provider"] = args.provider
    if args.model:
        metadata["model"] = args.model
    if args.labels.strip():
        metadata["labels"] = [label.strip() for label in args.labels.split(",") if label.strip()]
    if args.expected_output:
        metadata["expected_output"] = args.expected_output
    if args.json_schema_file:
        metadata["json_schema"] = json.loads(Path(args.json_schema_file).read_text(encoding="utf-8"))

    task = HarnessTask(
        task_type=args.task_type,
        input_path=args.input,
        output_dir=args.output_dir,
        document_type=args.document_type,
        metadata=metadata,
    )
    result = build_router().dispatch(task)
    if result.status != "ok":
        for error in result.errors:
            print(f"error: {error}")
        if result.metadata:
            print(json.dumps(result.metadata, ensure_ascii=False, indent=2))
        return 1

    for key, path in result.outputs.items():
        print(f"{key}: {path}")
    if result.metadata:
        print(json.dumps(result.metadata, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
