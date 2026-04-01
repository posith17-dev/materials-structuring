from __future__ import annotations

from collections.abc import Callable

from .policy import HarnessPolicy, default_policy
from .schemas import HarnessResult, HarnessTask

Executor = Callable[[HarnessTask], HarnessResult]


class HarnessRouter:
    def __init__(self, policy: HarnessPolicy | None = None) -> None:
        self.policy = policy or default_policy()
        self.executors: dict[str, Executor] = {}

    def register(self, engine: str, executor: Executor) -> None:
        self.executors[engine] = executor

    def dispatch(self, task: HarnessTask) -> HarnessResult:
        engines = [self.policy.resolve_engine(task.task_type), *self.policy.resolve_fallbacks(task.task_type)]
        attempted: list[str] = []
        collected_errors: list[str] = []
        for engine in engines:
            attempted.append(engine)
            executor = self.executors.get(engine)
            if executor is None:
                collected_errors.append(f"missing_executor:{engine}")
                continue
            result = executor(task)
            result.metadata.setdefault("attempted_engines", attempted.copy())
            if result.status == "ok":
                return result
            collected_errors.extend(result.errors)
        return HarnessResult(
            task_type=task.task_type,
            engine=engines[0] if engines else "unknown",
            status="error",
            errors=collected_errors or [f"No executor succeeded for task_type={task.task_type}"],
            metadata={"attempted_engines": attempted},
        )
