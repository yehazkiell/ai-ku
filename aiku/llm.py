"""Multi-provider LLM router.

Picks an inference backend based on configuration and falls back gracefully:

    OpenRouter -> Groq -> OpenAI -> g4f (free)

Every provider speaks the OpenAI chat-completions message format, so callers
only ever deal with ``[{"role": ..., "content": ...}]`` lists.
"""
from typing import Dict, List, Optional

import requests
from loguru import logger

from aiku.config import settings

# OpenAI-compatible HTTP endpoints keyed by provider name.
_OPENAI_COMPATIBLE = {
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "key": lambda: settings.openrouter_api_key,
        "model": "openai/gpt-4o-mini",
    },
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key": lambda: settings.groq_api_key,
        "model": "llama-3.3-70b-versatile",
    },
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "key": lambda: settings.openai_api_key,
        "model": "gpt-4o-mini",
    },
}


def _call_openai_compatible(provider: str, messages: List[Dict], model: Optional[str]) -> str:
    cfg = _OPENAI_COMPATIBLE[provider]
    api_key = cfg["key"]()
    if not api_key:
        raise RuntimeError(f"{provider} API key not configured")

    payload = {"model": model or settings.llm_model or cfg["model"], "messages": messages}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    resp = requests.post(cfg["url"], json=payload, headers=headers, timeout=settings.request_timeout)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def _call_g4f(messages: List[Dict]) -> str:
    """Free fallback using g4f, importing defensively at call time."""
    import g4f  # imported lazily so the package is optional

    last_error: Optional[Exception] = None
    # Resolve providers/models defensively: attributes differ across g4f versions.
    candidates = []
    for provider_name in ("Blackbox", "OperaAria", "You", "DDG"):
        provider = getattr(g4f.Provider, provider_name, None)
        if provider is not None:
            candidates.append(provider)

    model = getattr(getattr(g4f, "models", None), "default", None)
    for provider in candidates or [None]:
        try:
            kwargs = {"messages": messages}
            if provider is not None:
                kwargs["provider"] = provider
            if model is not None:
                kwargs["model"] = model
            result = g4f.ChatCompletion.create(**kwargs)
            if result:
                return result if isinstance(result, str) else "".join(result)
        except Exception as exc:  # pragma: no cover - network/provider dependent
            last_error = exc
            logger.error(f"g4f provider {getattr(provider, '__name__', provider)} failed: {exc}")
            continue
    raise RuntimeError(f"All g4f providers failed: {last_error}")


def _provider_order() -> List[str]:
    """Decide which providers to try and in what order."""
    forced = settings.llm_provider.lower()
    if forced in _OPENAI_COMPATIBLE:
        return [forced, "g4f"]
    if forced == "g4f":
        return ["g4f"]
    # auto: configured remote providers first, then free fallback
    return settings.configured_providers() + ["g4f"]


def chat(messages: List[Dict], model: Optional[str] = None) -> str:
    """Run a chat completion against the first working provider."""
    errors = []
    for provider in _provider_order():
        try:
            if provider == "g4f":
                return _call_g4f(messages)
            return _call_openai_compatible(provider, messages, model)
        except Exception as exc:
            errors.append(f"{provider}: {exc}")
            logger.error(f"LLM provider '{provider}' failed: {exc}")
            continue
    return f"Critical Error: all LLM providers failed ({'; '.join(errors)})."
