from __future__ import annotations

import argparse

from .executors import large_model_executor, rule_executor, small_model_executor
from .router import HarnessRouter
from .schemas import HarnessTask


DOCUMENT_TASK_MAP = {
    "test_certificate": "test_certificate_process",
    "msds": "msds_process",
}


def build_router() -> HarnessRouter:
    router = HarnessRouter()
    router.register("rule", rule_executor)
    router.register("small_model", small_model_executor)
    router.register("large_model", large_model_executor)
    return router


def main() -> int:
    parser = argparse.ArgumentParser(description="Common harness CLI")
    parser.add_argument(
        "--document-type",
        required=True,
        choices=sorted(DOCUMENT_TASK_MAP.keys()),
        help="Document family to process",
    )
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    args = parser.parse_args()

    task = HarnessTask(
        task_type=DOCUMENT_TASK_MAP[args.document_type],
        input_path=args.input,
        output_dir=args.output_dir,
        document_type=args.document_type,
    )
    result = build_router().dispatch(task)
    if result.status != "ok":
        for error in result.errors:
            print(f"error: {error}")
        return 1
    for key, path in result.outputs.items():
        print(f"{key}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
