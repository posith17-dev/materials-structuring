from __future__ import annotations

import json
from pathlib import Path

from ..local_fallback import deep_review_local
from ..model_client import call_model
from ..schemas import HarnessResult, HarnessTask


MODEL_BY_TASK = {
    "openai": {
        "compare_multi_doc": "gpt-5.4",
        "deep_review": "gpt-5.4",
    },
    "anthropic": {
        "compare_multi_doc": "claude-3-5-sonnet-latest",
        "deep_review": "claude-3-5-sonnet-latest",
    },
    "gemini": {
        "compare_multi_doc": "gemini-2.5-pro",
        "deep_review": "gemini-2.5-pro",
    },
}

PROVIDER_BY_TASK = {
    "compare_multi_doc": "openai",
    "deep_review": "openai",
}

PROVIDER_CHAIN_BY_TASK = {
    "compare_multi_doc": ["openai", "anthropic", "gemini"],
    "deep_review": ["openai", "anthropic", "gemini"],
}


def _provider_chain(task: HarnessTask) -> list[str]:
    providers = task.metadata.get("providers")
    if isinstance(providers, list) and providers:
        return [str(provider).strip() for provider in providers if str(provider).strip()]
    provider = str(task.metadata.get("provider") or PROVIDER_BY_TASK.get(task.task_type, "openai")).strip()
    if provider:
        return [provider]
    return PROVIDER_CHAIN_BY_TASK.get(task.task_type, ["openai", "anthropic", "gemini"])


def _default_model(task_type: str, provider: str) -> str:
    return MODEL_BY_TASK.get(provider, {}).get(task_type, "gpt-5.4")


def large_model_executor(task: HarnessTask) -> HarnessResult:
    prompt = str(task.metadata.get("prompt", "")).strip()
    if not prompt:
        return HarnessResult(
            task_type=task.task_type,
            engine="large_model",
            status="error",
            errors=["large_model task requires metadata.prompt"],
            metadata={
                "document_type": task.document_type,
                "recommended_model": _default_model(task.task_type, "openai"),
            },
        )

    provider_chain = _provider_chain(task)
    schema = task.metadata.get("json_schema")
    out_dir = Path(task.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    remote_errors: list[str] = []
    raw_response = None
    output_text = ""
    used_provider = ""
    for provider in provider_chain:
        model = str(task.metadata.get("model") or _default_model(task.task_type, provider))
        try:
            raw_response, output_text = call_model(
                provider=provider,
                prompt_text=prompt,
                model=model,
                json_schema=schema,
                timeout=300,
            )
            used_provider = provider
            break
        except Exception as exc:
            remote_errors.append(f"{provider}: {exc}")

    if raw_response is None:
        exc_text = " | ".join(remote_errors) if remote_errors else "remote model call failed"
        fallback_model = str(task.metadata.get("model") or _default_model(task.task_type, provider_chain[0]))
        if task.task_type not in {"compare_multi_doc", "deep_review"}:
            return HarnessResult(
                task_type=task.task_type,
                engine="large_model",
                status="error",
                errors=[exc_text],
                metadata={"document_type": task.document_type, "recommended_model": fallback_model},
            )
        output_text = deep_review_local(prompt, remote_error=exc_text)
        text_path = out_dir / "large_model_output.txt"
        text_path.write_text(output_text, encoding="utf-8")
        fallback_meta_path = out_dir / "large_model_fallback.json"
        fallback_meta_path.write_text(
            json.dumps(
                {
                    "status": "local_fallback_used",
                    "task_type": task.task_type,
                    "document_type": task.document_type,
                    "remote_model": fallback_model,
                    "providers": provider_chain,
                    "remote_error": exc_text,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return HarnessResult(
            task_type=task.task_type,
            engine="large_model",
            status="ok",
            outputs={
                "text": str(text_path),
                "fallback_meta": str(fallback_meta_path),
            },
            metadata={
                "document_type": task.document_type,
                "recommended_model": fallback_model,
                "providers": provider_chain,
                "fallback_used": True,
                "fallback_reason": exc_text,
            },
        )
    raw_path = out_dir / "large_model_raw.json"
    text_path = out_dir / "large_model_output.txt"
    raw_path.write_text(json.dumps(raw_response, ensure_ascii=False, indent=2), encoding="utf-8")
    text_path.write_text(output_text, encoding="utf-8")

    return HarnessResult(
        task_type=task.task_type,
        engine="large_model",
        status="ok",
        outputs={
            "raw_json": str(raw_path),
            "text": str(text_path),
        },
        metadata={
            "document_type": task.document_type,
            "recommended_model": str(task.metadata.get("model") or _default_model(task.task_type, used_provider)),
            "provider": used_provider,
            "providers": provider_chain,
            "expected_output": task.metadata.get("expected_output", ""),
            "fallback_used": False,
        },
    )
