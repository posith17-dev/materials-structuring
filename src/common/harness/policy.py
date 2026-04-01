from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HarnessPolicy:
    default_engine_by_task: dict[str, str] = field(default_factory=dict)
    fallback_order_by_task: dict[str, list[str]] = field(default_factory=dict)

    def resolve_engine(self, task_type: str) -> str:
        return self.default_engine_by_task.get(task_type, "rule")

    def resolve_fallbacks(self, task_type: str) -> list[str]:
        return self.fallback_order_by_task.get(task_type, [])


def default_policy() -> HarnessPolicy:
    return HarnessPolicy(
        default_engine_by_task={
            "test_certificate_process": "rule",
            "msds_process": "rule",
            "extract": "rule",
            "normalize": "rule",
            "validate": "rule",
            "report": "rule",
            "classify": "small_model",
            "summarize": "small_model",
            "draft": "small_model",
            "compare_multi_doc": "large_model",
            "deep_review": "large_model",
        },
        fallback_order_by_task={
            "test_certificate_process": [],
            "msds_process": [],
            "extract": [],
            "normalize": [],
            "validate": [],
            "report": [],
            "classify": ["large_model"],
            "summarize": ["large_model"],
            "draft": ["large_model"],
            "compare_multi_doc": [],
            "deep_review": [],
        },
    )
