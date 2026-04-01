from __future__ import annotations

from msds.main import process_file as process_msds_file
from test_certificate.main import process_file as process_test_certificate_file
from ..schemas import HarnessResult, HarnessTask


def rule_executor(task: HarnessTask) -> HarnessResult:
    if task.task_type == "test_certificate_process":
        outputs = process_test_certificate_file(task.input_path, task.output_dir)
        return HarnessResult(
            task_type=task.task_type,
            engine="rule",
            status="ok",
            outputs={key: str(path) for key, path in outputs.items()},
            metadata={"document_type": task.document_type},
        )
    if task.task_type == "msds_process":
        outputs = process_msds_file(task.input_path, task.output_dir)
        return HarnessResult(
            task_type=task.task_type,
            engine="rule",
            status="ok",
            outputs={key: str(path) for key, path in outputs.items()},
            metadata={"document_type": task.document_type},
        )

    return HarnessResult(
        task_type=task.task_type,
        engine="rule",
        status="error",
        errors=[f"Unsupported rule task_type={task.task_type}"],
        metadata={"document_type": task.document_type},
    )
