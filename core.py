"""High-level AI-KU API used by the CLI (`hazz.py`) and the HTTP server (`app.py`).

Thin wrappers around the orchestrator, vector memory, and tools. Heavy backends
(LLM providers, ChromaDB) are loaded lazily, so importing this module is cheap.
"""
import threading
import time

from loguru import logger

from aiku.agents.orchestrator import PERSONA, ROLE_PROMPTS, orchestrator
from aiku.config import settings
from aiku.memory.rag import memory_instance
from aiku.tools.image import generate_image
from aiku.tools.search import search_web


def get_ai_response(message, role="general", history=None, context=""):
    """RAG-augmented chat: retrieves relevant memory and respects role + history."""
    history = history or []
    system_msg = ROLE_PROMPTS.get(role, PERSONA)

    recalled = _recall_context(message)
    augmented = message
    extra = []
    if recalled:
        extra.append(f"RELEVANT MEMORY:\n{recalled}")
    if context:
        extra.append(f"ADDITIONAL CONTEXT:\n{context}")
    if extra:
        augmented = "\n\n".join(extra) + f"\n\nUSER MESSAGE:\n{message}"

    return orchestrator.call_llm(augmented, system_msg=system_msg, history=history)


def _recall_context(query):
    try:
        memories = memory_instance.query_memory(query, n_results=settings.memory_top_k)
    except Exception as e:
        logger.warning(f"Memory recall unavailable: {e}")
        return ""
    return "\n".join(f"- {m}" for m in memories) if memories else ""


def run_team_task(task, role="general"):
    return orchestrator.run_task(task, role=role)


def save_data(item):
    return memory_instance.add_memory(item)


def recall_data(query, n_results=None):
    return memory_instance.query_memory(query, n_results=n_results or settings.memory_top_k)


def start_scout_mode(interval=7200):
    """Background loop that periodically refreshes long-term knowledge."""

    def scout_loop():
        while True:
            try:
                info = search_web("Latest AI news")
                memory_instance.add_memory(f"Knowledge update: {info[:500]}")
            except Exception as e:
                logger.error(f"Scout mode error: {e}")
            time.sleep(interval)

    threading.Thread(target=scout_loop, daemon=True).start()
