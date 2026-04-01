from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TestCertificateRecord:
    document_name: str = ""
    issue_date: str = ""
    product_name: str = ""
    lot_no: str = ""
    item_name: str = ""
    measured_value: float | None = None
    unit: str = ""
    lower_spec: float | None = None
    upper_spec: float | None = None
    judgment: str = ""
    source_page: int | None = None
    raw_text: str = ""
    source_ref: str = ""


@dataclass
class ValidationIssue:
    rule: str
    severity: str
    message: str
    item_name: str = ""
    source_page: int | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentBundle:
    source_file: str
    document_type: str = "test_certificate"
    document_name: str = ""
    issue_date: str = ""
    product_name: str = ""
    lot_no: str = ""
    raw_pages: list[str] = field(default_factory=list)
    records: list[TestCertificateRecord] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)
