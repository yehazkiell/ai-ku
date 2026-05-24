# AI-Ku Development Guide

Welcome, Agent! You are working on **AI-Ku**, a professional-grade AI Suite that provides high-quality text and image generation 100% free and without API keys.

## 🏗 Architecture Overview

AI-Ku follows a dual-engine architecture:
1.  **Standard Engine (Pollinations)**: High availability, fast response times, supports various models (OpenAI, Mistral, Llama). Used for standard chat and all image generation.
2.  **Ultra IQ Engine (g4f)**: Advanced reasoning engine using the `g4f` library. Optimized for logic-heavy tasks and provides a non-Pollination alternative.

## 🛠 Tech Stack
-   **Backend**: Flask (Python)
-   **Frontend**: Vanilla JavaScript + CSS Variables + Jinja2
-   **Libraries**:
    -   `marked.js`: Markdown rendering.
    -   `DOMPurify`: HTML sanitization (Critical for safety).
    -   `highlight.js`: Code syntax highlighting.
    -   `FontAwesome`: Icons.

## 📝 Coding Standards
-   **No API Keys**: Under no circumstances should an API key be required or hardcoded. This is the core principle of the project.
-   **XSS Protection**: Always sanitize AI-generated content using `DOMPurify` before injecting into the DOM.
-   **State Persistence**: User preferences (theme, sessions, history) must be stored in `localStorage` to ensure a consistent experience without a database.

## 🧪 Testing
-   Verify changes using **Playwright**.
-   Always check both "Standard" and "Ultra IQ" engines when modifying the chat logic.
-   Ensure responsive design works for mobile (max-width: 768px).

## 🚀 Deployment
The app is designed to be easily deployable on platforms like Render or Heroku.
-   `app.py` is the entry point.
-   Ensure `requirements.txt` is up to date with `g4f`, `flask`, and `requests`.

---
*Created by Jules, Senior AI Engineer.*
