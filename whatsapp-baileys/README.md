# AI-KU WhatsApp Bridge (Baileys)

Connect AI-KU to WhatsApp **without any API key, Twilio, or Meta** — it logs in
by scanning a QR code (WhatsApp "Linked devices") using
[Baileys](https://github.com/WhiskeySockets/Baileys), then forwards every
incoming message to the AI-KU REST API and replies with the answer.

## Setup

1. Start the AI-KU API server first (from the repo root):
   ```bash
   python3 app.py        # serves http://localhost:5000
   ```
2. Configure and run the bridge:
   ```bash
   cd whatsapp-baileys
   cp .env.example .env   # set AIKU_API_URL / AIKU_API_KEY if not default
   npm install
   npm start
   ```
3. A QR code appears in the terminal. Open WhatsApp on your phone →
   **Settings → Linked devices → Link a device** → scan it.
4. Once it prints `AI-KU WhatsApp bridge is online.`, message the linked number.

## Behaviour

- **Private chats:** every text message gets an AI-KU reply.
- **Group chats:** only messages starting with `AIKU_WA_GROUP_PREFIX` (default
  `.ai`) are answered, e.g. `.ai what's the weather like on Mars?`. Set the
  prefix to empty to answer everything in groups.
- A short rolling conversation history is kept per chat and sent to
  `/api/v1/chat` so replies stay contextual.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `AIKU_API_URL` | `http://localhost:5000` | Base URL of the AI-KU API. |
| `AIKU_API_KEY` | `aiku_master_key_123` | Must match the server's `AIKU_API_KEY`. |
| `AIKU_WA_GROUP_PREFIX` | `.ai` | Prefix required to trigger replies in groups. |
| `AIKU_WA_AUTH_DIR` | `./auth_state` | Where the WhatsApp session is stored (keep private). |

> The `auth_state/` folder holds your WhatsApp login — it is git-ignored. Never
> commit or share it. Requires Node.js 18+ (for the global `fetch`).
