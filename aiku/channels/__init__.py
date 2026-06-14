"""Messaging channels that expose AI-KU over external surfaces.

Each channel (Telegram, WhatsApp, web chat) is a thin adapter that turns an
incoming text message into a reply via :func:`aiku.channels.handler.reply_to`.
"""
