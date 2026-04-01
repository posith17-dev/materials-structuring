from __future__ import annotations

import json
import os
from pathlib import Path
import urllib.request
from urllib.error import HTTPError


ENV_CANDIDATES = [
    Path("/home/ubuntu/trading-system/config/secrets.env"),
    Path("/home/ubuntu/trading-bot/.env"),
]


def load_env_fallback() -> None:
    for env_path in ENV_CANDIDATES:
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            if key and value and key not in os.environ:
                os.environ[key] = value


def response_output_text(data: dict) -> str:
    output = data.get("output", [])
    texts: list[str] = []
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content", [])
            if not isinstance(content, list):
                continue
            for part in content:
                if not isinstance(part, dict):
                    continue
                if part.get("type") == "output_text":
                    value = part.get("text", "")
                    if isinstance(value, str) and value.strip():
                        texts.append(value.strip())
    return "\n".join(texts).strip()


def call_openai_responses(
    *,
    prompt_text: str,
    model: str,
    json_schema: dict | None = None,
    timeout: int = 180,
) -> dict:
    load_env_fallback()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing")

    body: dict = {
        "model": model,
        "input": prompt_text,
    }
    if json_schema:
        body["text"] = {
            "format": {
                "type": "json_schema",
                "name": json_schema.get("name", "harness_response"),
                "schema": json_schema["schema"],
                "strict": True,
            }
        }

    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body, ensure_ascii=True).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"openai_http_error status={exc.code} body={body_text[:1200]}") from exc


def call_anthropic_messages(
    *,
    prompt_text: str,
    model: str,
    timeout: int = 180,
) -> dict:
    load_env_fallback()
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY missing")

    body = {
        "model": model,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt_text}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body, ensure_ascii=True).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"anthropic_http_error status={exc.code} body={body_text[:1200]}") from exc


def anthropic_output_text(data: dict) -> str:
    content = data.get("content", [])
    texts: list[str] = []
    if isinstance(content, list):
        for part in content:
            if not isinstance(part, dict):
                continue
            if part.get("type") == "text":
                text = part.get("text", "")
                if isinstance(text, str) and text.strip():
                    texts.append(text.strip())
    return "\n".join(texts).strip()


def call_gemini_generate_content(
    *,
    prompt_text: str,
    model: str,
    timeout: int = 180,
) -> dict:
    load_env_fallback()
    api_key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY or GOOGLE_API_KEY missing")

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text},
                ]
            }
        ]
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
        data=json.dumps(body, ensure_ascii=True).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"gemini_http_error status={exc.code} body={body_text[:1200]}") from exc


def gemini_output_text(data: dict) -> str:
    candidates = data.get("candidates", [])
    texts: list[str] = []
    if isinstance(candidates, list):
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            content = candidate.get("content", {})
            if not isinstance(content, dict):
                continue
            parts = content.get("parts", [])
            if not isinstance(parts, list):
                continue
            for part in parts:
                if not isinstance(part, dict):
                    continue
                text = part.get("text", "")
                if isinstance(text, str) and text.strip():
                    texts.append(text.strip())
    return "\n".join(texts).strip()


def call_model(
    *,
    provider: str,
    prompt_text: str,
    model: str,
    json_schema: dict | None = None,
    timeout: int = 180,
) -> tuple[dict, str]:
    provider = provider.strip().lower()
    if provider == "openai":
        data = call_openai_responses(prompt_text=prompt_text, model=model, json_schema=json_schema, timeout=timeout)
        return data, response_output_text(data)
    if provider == "anthropic":
        data = call_anthropic_messages(prompt_text=prompt_text, model=model, timeout=timeout)
        return data, anthropic_output_text(data)
    if provider == "gemini":
        data = call_gemini_generate_content(prompt_text=prompt_text, model=model, timeout=timeout)
        return data, gemini_output_text(data)
    raise RuntimeError(f"Unsupported provider: {provider}")
