"""Centralized configuration for AI-KU.

Reads every environment variable in one place, validates it, and exposes a
single ``settings`` object used across the CLI, the API server, and the agents.
"""
import os
from dataclasses import dataclass, field
from typing import List, Optional

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

DEFAULT_API_KEY = "aiku_master_key_123"


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        logger.warning(f"Invalid integer for {name}={raw!r}, using default {default}")
        return default


def mask_secret(value: Optional[str]) -> str:
    """Return a masked representation of a secret, safe for logs."""
    if not value:
        return "<unset>"
    if len(value) <= 8:
        return "****"
    return f"{value[:4]}…{value[-4:]}"


@dataclass
class Settings:
    # Core
    api_key: str = field(default_factory=lambda: os.getenv("AIKU_API_KEY", DEFAULT_API_KEY))
    env: str = field(default_factory=lambda: os.getenv("AIKU_ENV", "development"))

    # LLM providers (optional)
    openrouter_api_key: str = field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    groq_api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))

    # Provider routing / model selection
    llm_provider: str = field(default_factory=lambda: os.getenv("AIKU_LLM_PROVIDER", "auto"))
    llm_model: str = field(default_factory=lambda: os.getenv("AIKU_LLM_MODEL", "gpt-4o-mini"))
    request_timeout: int = field(default_factory=lambda: _get_int("AIKU_REQUEST_TIMEOUT", 60))

    # Agent behaviour
    max_iterations: int = field(default_factory=lambda: _get_int("AIKU_MAX_ITERATIONS", 6))
    enable_reflection: bool = field(default_factory=lambda: _get_bool("AIKU_ENABLE_REFLECTION", True))

    # Memory / RAG
    memory_path: str = field(default_factory=lambda: os.getenv("AIKU_MEMORY_PATH", "./chroma_db"))
    memory_top_k: int = field(default_factory=lambda: _get_int("AIKU_MEMORY_TOP_K", 4))

    # Server
    host: str = field(default_factory=lambda: os.getenv("AIKU_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: _get_int("AIKU_PORT", 5000))

    @property
    def is_production(self) -> bool:
        return self.env.lower() in ("prod", "production")

    def configured_providers(self) -> List[str]:
        """Names of remote providers that have an API key configured."""
        providers = []
        if self.openrouter_api_key:
            providers.append("openrouter")
        if self.groq_api_key:
            providers.append("groq")
        if self.openai_api_key:
            providers.append("openai")
        return providers

    def validate(self) -> List[str]:
        """Return a list of human-readable configuration warnings."""
        warnings: List[str] = []
        if self.is_production and self.api_key == DEFAULT_API_KEY:
            warnings.append(
                "AIKU_API_KEY is still the default value in production. "
                "Set a strong AIKU_API_KEY before exposing the API."
            )
        if not self.configured_providers():
            warnings.append(
                "No remote LLM provider key set (OPENROUTER/GROQ/OPENAI). "
                "Falling back to free g4f providers, which may be less stable."
            )
        if self.max_iterations < 1:
            warnings.append("AIKU_MAX_ITERATIONS must be >= 1; clamping to 1.")
            self.max_iterations = 1
        return warnings

    def summary(self) -> str:
        """A masked, human-readable summary safe to print."""
        lines = [
            f"env                = {self.env}",
            f"api_key            = {mask_secret(self.api_key)}",
            f"llm_provider       = {self.llm_provider}",
            f"llm_model          = {self.llm_model}",
            f"max_iterations     = {self.max_iterations}",
            f"reflection         = {self.enable_reflection}",
            f"memory_path        = {self.memory_path}",
            f"memory_top_k       = {self.memory_top_k}",
            f"remote_providers   = {', '.join(self.configured_providers()) or 'none (g4f fallback)'}",
            f"openrouter_api_key = {mask_secret(self.openrouter_api_key)}",
            f"groq_api_key       = {mask_secret(self.groq_api_key)}",
            f"openai_api_key     = {mask_secret(self.openai_api_key)}",
        ]
        return "\n".join(lines)


settings = Settings()

for _warning in settings.validate():
    logger.warning(_warning)
