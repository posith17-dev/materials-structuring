from __future__ import annotations

import re


def _clean_prompt(prompt: str) -> str:
    text = re.sub(r"\s+", " ", prompt).strip()
    return text


def summarize_local(prompt: str) -> str:
    text = _clean_prompt(prompt)
    if not text:
        return "요약할 입력이 없습니다."
    if ":" in text:
        text = text.split(":", 1)[-1].strip()
    text = text.rstrip(". ")
    if len(text) > 120:
        text = text[:117].rstrip() + "..."
    return f"요약: {text}."


def classify_local(prompt: str, labels: list[str] | None = None) -> str:
    text = _clean_prompt(prompt).lower()
    labels = labels or []
    for label in labels:
        if label.lower() in text:
            return label
    return labels[0] if labels else "unknown"


def draft_local(prompt: str) -> str:
    text = _clean_prompt(prompt)
    if not text:
        return "초안 생성 입력이 없습니다."
    return f"초안:\n{text}"


def deep_review_local(prompt: str, remote_error: str = "") -> str:
    text = _clean_prompt(prompt)
    prefix = "원격 모델 호출 실패로 로컬 검토 메모를 생성했습니다."
    if remote_error:
        prefix += f" 오류: {remote_error}"
    if len(text) > 200:
        text = text[:197].rstrip() + "..."
    return f"{prefix}\n검토 대상: {text}"
