from __future__ import annotations

from .models import TestCertificateRecord, ValidationIssue


def validate_record(record: TestCertificateRecord) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if not record.item_name:
        issues.append(
            ValidationIssue(
                rule="REQUIRED_FIELD_MISSING",
                severity="high",
                message="필수 필드 item_name 누락",
                item_name=record.item_name,
                source_page=record.source_page,
            )
        )

    if record.measured_value is None:
        issues.append(
            ValidationIssue(
                rule="NUMERIC_PARSE_FAILED",
                severity="medium",
                message="측정값 숫자 파싱 실패",
                item_name=record.item_name,
                source_page=record.source_page,
            )
        )

    if record.lower_spec is not None and record.measured_value is not None and record.measured_value < record.lower_spec:
        issues.append(
            ValidationIssue(
                rule="OUT_OF_RANGE_LOW",
                severity="high",
                message="측정값이 하한 미만",
                item_name=record.item_name,
                source_page=record.source_page,
                details={"measured_value": record.measured_value, "lower_spec": record.lower_spec},
            )
        )

    if record.upper_spec is not None and record.measured_value is not None and record.measured_value > record.upper_spec:
        issues.append(
            ValidationIssue(
                rule="OUT_OF_RANGE_HIGH",
                severity="high",
                message="측정값이 상한 초과",
                item_name=record.item_name,
                source_page=record.source_page,
                details={"measured_value": record.measured_value, "upper_spec": record.upper_spec},
            )
        )

    if not record.unit:
        issues.append(
            ValidationIssue(
                rule="REQUIRED_FIELD_MISSING",
                severity="medium",
                message="단위 누락",
                item_name=record.item_name,
                source_page=record.source_page,
            )
        )

    return issues


def validate_records(records: list[TestCertificateRecord]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    seen: dict[str, float | None] = {}
    has_any_spec_or_judgment = False
    for record in records:
        issues.extend(validate_record(record))
        if record.lower_spec is not None or record.upper_spec is not None or record.judgment:
            has_any_spec_or_judgment = True
        if record.item_name:
            prev = seen.get(record.item_name)
            if prev is not None and record.measured_value is not None and prev != record.measured_value:
                issues.append(
                    ValidationIssue(
                        rule="DUPLICATE_ITEM_CONFLICT",
                        severity="high",
                        message="동일 항목의 값이 문서 내에서 상충함",
                        item_name=record.item_name,
                        source_page=record.source_page,
                        details={"previous_value": prev, "current_value": record.measured_value},
                    )
                )
            else:
                seen[record.item_name] = record.measured_value
    if records and not has_any_spec_or_judgment:
        issues.append(
            ValidationIssue(
                rule="DOCUMENT_SPEC_MISSING",
                severity="medium",
                message="문서 전체에 규격값 또는 판정 정보가 없어 자동 판정 불가",
                source_page=records[0].source_page,
            )
        )
    return issues
