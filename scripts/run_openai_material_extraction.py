#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import urllib.request
from urllib.error import HTTPError

from material_property_experiment import extract_text


ENV_CANDIDATES = [
    Path("/home/ubuntu/trading-system/config/secrets.env"),
    Path("/home/ubuntu/trading-bot/.env"),
]

DEFAULT_MODEL = "gpt-4o-mini"

JSON_SCHEMA = {
    "name": "material_property_records",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "records": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "material_name": {"type": "string"},
                        "composition": {"type": "string"},
                        "property_name": {"type": "string"},
                        "property_value": {"type": "string"},
                        "property_unit": {"type": "string"},
                        "test_condition": {"type": "string"},
                        "source_page": {"type": "string"},
                        "source_excerpt": {"type": "string"},
                    },
                    "required": [
                        "material_name",
                        "composition",
                        "property_name",
                        "property_value",
                        "property_unit",
                        "test_condition",
                        "source_page",
                        "source_excerpt",
                    ],
                },
            }
        },
        "required": ["records"],
    },
}


def _load_env_fallback() -> None:
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


def _response_output_text(data: dict) -> str:
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


def _call_openai(prompt_text: str, model: str) -> dict:
    _load_env_fallback()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing")

    body = {
        "model": model,
        "input": prompt_text,
        "text": {
            "format": {
                "type": "json_schema",
                "name": JSON_SCHEMA["name"],
                "schema": JSON_SCHEMA["schema"],
                "strict": True,
            }
        },
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
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"openai_http_error status={exc.code} body={body[:1200]}") from exc

    text = _response_output_text(data)
    if not text:
        raise RuntimeError("OpenAI response had no output_text")
    return json.loads(text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", required=True, help="Path to experiment JSON stub")
    parser.add_argument("--llm-output", required=True, help="Path to write raw LLM JSON")
    parser.add_argument("--merged-output", required=True, help="Path to write merged output JSON")
    parser.add_argument("--model", default="", help="Optional override model name")
    parser.add_argument(
        "--max-chars",
        type=int,
        default=12000,
        help="Maximum number of source characters to send to the model",
    )
    args = parser.parse_args()

    experiment_path = Path(args.experiment)
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    prompt_file = Path(experiment["prompt_file"])
    source_file = Path(experiment["source_file"])

    extracted_text = extract_text(source_file)
    instructions = prompt_file.read_text(encoding="utf-8")
    model = args.model.strip() or os.getenv("OPENAI_MODEL", "").strip() or DEFAULT_MODEL

    source_text = extracted_text[: max(1000, args.max_chars)]

    prompt = (
        f"{instructions}\n\n"
        "[Source file]\n"
        f"{source_file}\n\n"
        "[Paper text]\n"
        f"{source_text}\n"
    )

    llm_payload = _call_openai(prompt, model=model)

    llm_output_path = Path(args.llm_output)
    llm_output_path.parent.mkdir(parents=True, exist_ok=True)
    llm_output_path.write_text(json.dumps(llm_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    merged = dict(experiment)
    merged["status"] = "llm_extraction_completed"
    merged["records"] = llm_payload.get("records", [])
    merged["llm_model"] = model

    merged_output_path = Path(args.merged_output)
    merged_output_path.parent.mkdir(parents=True, exist_ok=True)
    merged_output_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"llm_output_path={llm_output_path}")
    print(f"merged_output_path={merged_output_path}")
    print(f"records={len(merged['records'])}")
    print(f"model={model}")
    print(f"chars_sent={len(source_text)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
