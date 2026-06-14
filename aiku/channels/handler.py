"""Shared brain for every messaging channel.

Channels (Telegram, WhatsApp, web chat) all funnel incoming messages through
:func:`reply_to`, which keeps a short rolling history per conversation and
delegates to the RAG-augmented chat in ``core.get_ai_response``.
"""
import threading
from collections import defaultdict, deque
from typing import Deque, Dict, List

from loguru import logger

# Keep the last N turns (user+assistant) per conversation to bound memory/context.
_MAX_TURNS = 10
_histories: Dict[str, Deque[dict]] = defaultdict(lambda: deque(maxlen=_MAX_TURNS * 2))
_lock = threading.Lock()

GREETING = (
    "👋 Hi, I'm AI-KU. Ask me anything, or send /reset to clear our conversation."
)


def _history_for(session_id: str) -> List[dict]:
    with _lock:
        return list(_histories[session_id])


def _remember(session_id: str, role: str, content: str) -> None:
    with _lock:
        _histories[session_id].append({"role": role, "content": content})


def reset(session_id: str) -> None:
    """Forget the rolling history for a conversation."""
    with _lock:
        _histories.pop(session_id, None)


def reply_to(text: str, session_id: str = "default", role: str = "general") -> str:
    """Return AI-KU's reply to ``text`` for the given conversation.

    Handles the ``/reset`` and ``/start`` control commands so every channel
    behaves consistently. History is per ``session_id`` (e.g. chat id).
    """
    text = (text or "").strip()
    if not text:
        return "Please send a text message."

    command = text.lower()
    if command in ("/start", "/help"):
        return GREETING
    if command == "/reset":
        reset(session_id)
        return "Conversation cleared. ✨"

    # Imported lazily so importing this module never pulls in heavy LLM backends.
    from core import get_ai_response

    history = _history_for(session_id)
    try:
        answer = get_ai_response(text, role=role, history=history)
    except Exception as exc:  # never crash a channel on a model failure
        logger.error(f"channel handler failed for session {session_id}: {exc}")
        return "Sorry, I hit an error while thinking. Please try again."

    _remember(session_id, "user", text)
    _remember(session_id, "assistant", answer)
    return answer
