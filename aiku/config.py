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

    # Local / self-hosted model — any OpenAI-compatible /v1 endpoint
    # (Ollama, LocalAI, LM Studio, vLLM, jan, llama.cpp server...).
    # No API key needed for most local servers, so this is the "own model,
    # no API key" path. Default points at Ollama's OpenAI-compatible endpoint.
    local_base_url: str = field(default_factory=lambda: os.getenv("AIKU_LOCAL_BASE_URL", "http://localhost:11434/v1"))
    local_model: str = field(default_factory=lambda: os.getenv("AIKU_LOCAL_MODEL", "llama3.2"))
    local_api_key: str = field(default_factory=lambda: os.getenv("AIKU_LOCAL_API_KEY", ""))
    use_local: bool = field(default_factory=lambda: _get_bool("AIKU_USE_LOCAL", False))

    # Provider routing / model selection
    llm_provider: str = field(default_factory=lambda: os.getenv("AIKU_LLM_PROVIDER", "auto"))
    # Empty by default so each provider's own default model is used (see aiku/llm.py).
    llm_model: str = field(default_factory=lambda: os.getenv("AIKU_LLM_MODEL", ""))
    request_timeout: int = field(default_factory=lambda: _get_int("AIKU_REQUEST_TIMEOUT", 60))

    # Agent behaviour
    max_iterations: int = field(default_factory=lambda: _get_int("AIKU_MAX_ITERATIONS", 6))
    enable_reflection: bool = field(default_factory=lambda: _get_bool("AIKU_ENABLE_REFLECTION", True))

    # Tool safety / sandboxing
    # Root that file tools (read/write/list) are confined to. Empty = current
    # working directory, resolved per call so the agent can never escape it.
    workspace_dir: str = field(default_factory=lambda: os.getenv("AIKU_WORKSPACE_DIR", ""))
    max_file_read_bytes: int = field(default_factory=lambda: _get_int("AIKU_MAX_FILE_READ_BYTES", 100_000))
    # Master switch for the agent's shell tool. Turn off to forbid shell entirely.
    allow_shell: bool = field(default_factory=lambda: _get_bool("AIKU_ALLOW_SHELL", True))

    # Memory / RAG
    memory_path: str = field(default_factory=lambda: os.getenv("AIKU_MEMORY_PATH", "./chroma_db"))
    memory_top_k: int = field(default_factory=lambda: _get_int("AIKU_MEMORY_TOP_K", 4))

    # Server
    host: str = field(default_factory=lambda: os.getenv("AIKU_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: _get_int("AIKU_PORT", 5000))

    # Messaging channels (all optional)
    telegram_bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    twilio_auth_token: str = field(default_factory=lambda: os.getenv("TWILIO_AUTH_TOKEN", ""))
    whatsapp_token: str = field(default_factory=lambda: os.getenv("WHATSAPP_TOKEN", ""))
    whatsapp_phone_number_id: str = field(default_factory=lambda: os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""))
    whatsapp_verify_token: str = field(default_factory=lambda: os.getenv("WHATSAPP_VERIFY_TOKEN", "aiku-verify"))

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

    def enabled_channels(self) -> List[str]:
        """Names of messaging channels that have the needed credentials set."""
        channels = ["web"]  # web chat only needs the API key, always available
        if self.telegram_bot_token:
            channels.append("telegram")
        if self.whatsapp_token and self.whatsapp_phone_number_id:
            channels.append("whatsapp_cloud")
        # Twilio replies via TwiML and needs no outbound token, so it's always reachable.
        channels.append("whatsapp_twilio")
        return channels

    def validate(self) -> List[str]:
        """Return a list of human-readable configuration warnings."""
        warnings: List[str] = []
        if self.is_production and self.api_key == DEFAULT_API_KEY:
            warnings.append(
                "AIKU_API_KEY is still the default value in production. "
                "Set a strong AIKU_API_KEY before exposing the API."
            )
        if not self.configured_providers() and not self.use_local:
            warnings.append(
                "No remote LLM provider key set (OPENROUTER/GROQ/OPENAI) and "
                "AIKU_USE_LOCAL is off. Falling back to free g4f providers, "
                "which may be less stable."
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
            f"llm_model          = {self.llm_model or '(provider default)'}",
            f"max_iterations     = {self.max_iterations}",
            f"reflection         = {self.enable_reflection}",
            f"workspace_dir      = {self.workspace_dir or '(cwd)'}",
            f"allow_shell        = {self.allow_shell}",
            f"memory_path        = {self.memory_path}",
            f"memory_top_k       = {self.memory_top_k}",
            f"remote_providers   = {', '.join(self.configured_providers()) or 'none (g4f fallback)'}",
            f"local_model        = {self.local_model} @ {self.local_base_url}" + (" (enabled)" if self.use_local else ""),
            f"channels           = {', '.join(self.enabled_channels())}",
            f"telegram_bot_token = {mask_secret(self.telegram_bot_token)}",
            f"whatsapp_token     = {mask_secret(self.whatsapp_token)}",
            f"openrouter_api_key = {mask_secret(self.openrouter_api_key)}",
            f"groq_api_key       = {mask_secret(self.groq_api_key)}",
            f"openai_api_key     = {mask_secret(self.openai_api_key)}",
        ]
        return "\n".join(lines)


settings = Settings()

for _warning in settings.validate():
    logger.warning(_warning)
