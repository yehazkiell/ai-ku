"""Telegram bot for AI-KU using long polling (no public webhook required).

Run it with::

    python3 -m aiku.channels.telegram_bot

Requires ``TELEGRAM_BOT_TOKEN`` (get one from @BotFather). Every incoming
message is answered by :func:`aiku.channels.handler.reply_to`, keyed by chat id
so each chat keeps its own short history.
"""
import sys
import time

import requests
from loguru import logger

from aiku.channels.handler import reply_to
from aiku.config import settings

API_BASE = "https://api.telegram.org/bot{token}/{method}"
# Telegram caps a single message at 4096 chars.
_MAX_LEN = 4096


def _call(method: str, **params):
    url = API_BASE.format(token=settings.telegram_bot_token, method=method)
    resp = requests.post(url, json=params, timeout=settings.request_timeout + 35)
    resp.raise_for_status()
    return resp.json()


def send_message(chat_id: int, text: str) -> None:
    for i in range(0, len(text) or 1, _MAX_LEN):
        _call("sendMessage", chat_id=chat_id, text=text[i:i + _MAX_LEN] or "(empty)")


def _handle_update(update: dict) -> None:
    message = update.get("message") or update.get("edited_message")
    if not message:
        return
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")
    if chat_id is None or not text:
        return
    logger.info(f"[telegram] {chat_id}: {text[:80]}")
    answer = reply_to(text, session_id=f"tg:{chat_id}")
    send_message(chat_id, answer)


def run() -> int:
    """Start the long-polling loop. Returns a process exit code."""
    if not settings.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN is not set. Add it to your .env first.")
        return 1

    me = _call("getMe").get("result", {})
    logger.info(f"AI-KU Telegram bot online as @{me.get('username', '?')}")

    offset = None
    while True:
        try:
            params = {"timeout": 30}
            if offset is not None:
                params["offset"] = offset
            data = _call("getUpdates", **params)
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                try:
                    _handle_update(update)
                except Exception as exc:
                    logger.error(f"[telegram] failed to handle update: {exc}")
        except KeyboardInterrupt:
            logger.info("Telegram bot stopped.")
            return 0
        except Exception as exc:
            logger.error(f"[telegram] polling error: {exc}; retrying in 3s")
            time.sleep(3)


if __name__ == "__main__":
    sys.exit(run())
