"""WhatsApp adapters for AI-KU.

Two providers are supported; pick whichever you have access to:

* **Twilio** – the Flask route receives a form POST and replies with TwiML.
  No outbound credentials are needed just to answer an incoming message.
* **Meta WhatsApp Cloud API** – the Flask route verifies the webhook (GET) and
  receives messages (POST), then replies via the Graph API using
  ``WHATSAPP_TOKEN`` + ``WHATSAPP_PHONE_NUMBER_ID``.

This module is pure logic (parsing/formatting/sending); the HTTP routes live in
``app.py`` so they share the app's rate limiting and error handling.
"""
from typing import List, Optional, Tuple
from xml.sax.saxutils import escape

import requests
from loguru import logger

from aiku.config import settings

GRAPH_URL = "https://graph.facebook.com/v21.0/{phone_id}/messages"


# --- Twilio --------------------------------------------------------------
def parse_twilio(form) -> Tuple[str, str]:
    """Extract (sender, body) from a Twilio webhook form payload."""
    return form.get("From", ""), (form.get("Body", "") or "").strip()


def twiml_reply(text: str) -> str:
    """Build a TwiML response that sends ``text`` back to the user."""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f"<Response><Message>{escape(text)}</Message></Response>"
    )


# --- Meta WhatsApp Cloud API --------------------------------------------
def meta_verify(mode: Optional[str], token: Optional[str], challenge: Optional[str]) -> Optional[str]:
    """Return ``challenge`` when Meta's webhook verification handshake succeeds."""
    if mode == "subscribe" and token and token == settings.whatsapp_verify_token:
        return challenge
    return None


def parse_meta(payload: dict) -> List[Tuple[str, str]]:
    """Extract a list of (sender, text) pairs from a Meta webhook payload."""
    out: List[Tuple[str, str]] = []
    for entry in (payload or {}).get("entry", []):
        for change in entry.get("changes", []):
            for msg in change.get("value", {}).get("messages", []):
                if msg.get("type") == "text":
                    out.append((msg.get("from", ""), msg.get("text", {}).get("body", "")))
    return out


def meta_send(to: str, text: str) -> bool:
    """Send a text message via the Meta Graph API. Returns success."""
    if not (settings.whatsapp_token and settings.whatsapp_phone_number_id):
        logger.error("WhatsApp Cloud API not configured (WHATSAPP_TOKEN / WHATSAPP_PHONE_NUMBER_ID).")
        return False
    url = GRAPH_URL.format(phone_id=settings.whatsapp_phone_number_id)
    headers = {"Authorization": f"Bearer {settings.whatsapp_token}"}
    body = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text[:4096]},
    }
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=settings.request_timeout)
        resp.raise_for_status()
        return True
    except Exception as exc:
        logger.error(f"WhatsApp send failed: {exc}")
        return False
