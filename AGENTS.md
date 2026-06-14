# AI-Ku Technical Architecture (CLI Only)

## Overview
This repository is a pure CLI application providing advanced LLM capabilities. It uses a dual-engine approach to bypass API key requirements while maintaining high intelligence.

## Core Components
- `core.py`: Logic for API calls, web search integration, and image generation.
- `hazz.py`: The main entry point. Handles the terminal UI, file extraction, and command routing.

## Dependencies
- `g4f`: Provides access to high-IQ models (OperaAria).
- `duckduckgo-search`: Real-time information retrieval.
- `PyPDF2`: Text extraction from documents.
- `requests`: General API interaction.

## Key Developer Commands
- Run CLI: `python3 hazz.py`
- Verify Core: `python3 -c "import core; print('OK')"`
