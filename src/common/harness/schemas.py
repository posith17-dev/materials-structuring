from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class HarnessTask:
    task_type: str
    input_path: str
    output_dir: str
    document_type: str = "generic"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HarnessResult:
    task_type: str
    engine: str
    status: str
    outputs: dict[str, str] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
