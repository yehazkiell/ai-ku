# AI-Ku Technical Architecture

## Overview
AI-KU is an autonomous AI agent (Manus / Devin / Jules style) exposed via a CLI
and a Flask REST API. It runs a Plan → Act → Observe → Reflect loop over a set of
tools, with RAG-backed long-term memory and a multi-provider LLM router.

## Core Components
- `hazz.py`: CLI entry point and command routing.
- `app.py`: Flask REST API (chat, agent, image, memory, health, metrics).
- `core.py`: High-level API used by both interfaces.
- `aiku/config.py`: Centralized settings read from environment variables.
- `aiku/llm.py`: Multi-provider LLM router (OpenRouter → Groq → OpenAI → g4f).
- `aiku/agents/orchestrator.py`: Autonomous Plan→Act→Observe→Reflect loop.
- `aiku/memory/rag.py`: ChromaDB vector memory (lazy-loaded).
- `aiku/tools/`: terminal, files, sandbox, search, image, browser, git.

## Configuration
All runtime configuration is via environment variables (see `.env.example` and
the README). Secrets are masked in logs/summaries via `aiku.config.mask_secret`.

## Dependencies
- `flask`, `flask-limiter`, `pydantic`: API server & validation.
- `chromadb`, `sentence-transformers`: vector memory (RAG).
- `requests`: remote LLM providers.
- `g4f`: free LLM fallback. `duckduckgo-search`: web search. `PyPDF2`: documents.

## Key Developer Commands
- Run CLI: `python3 hazz.py`
- Run API: `python3 app.py`
- Run tests: `python3 -m unittest discover tests`
- Verify Core: `python3 -c "import core; print('OK')"`
- Show config: `python3 -c "from aiku.config import settings; print(settings.summary())"`
