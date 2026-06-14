import os

from flask import Flask, request, jsonify, Response, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
from loguru import logger

from core import (
    get_ai_response,
    run_team_task,
    generate_image,
    save_data,
    recall_data,
)
from aiku.config import settings
from aiku.channels.handler import reply_to, GREETING
from aiku.channels import whatsapp

WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
# Endpoints reachable without an X-API-KEY (they are public or self-authenticated).
PUBLIC_ENDPOINTS = ("health", "metrics", "web_index", "twilio_webhook", "whatsapp_webhook")

app = Flask(__name__)
API_KEY = settings.api_key

for _warning in settings.validate():
    logger.warning(_warning)

# Robust rate limiting with Redis fallback option (defaulting to memory)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5000 per day", "500 per hour"],
    storage_uri="memory://",
)


# Pydantic models for strict request validation
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    role: Optional[str] = "general"
    history: Optional[List[dict]] = []


class AgentRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=5000)
    role: Optional[str] = "general"


class ImageRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    width: Optional[int] = Field(1024, ge=64, le=4096)
    height: Optional[int] = Field(1024, ge=64, le=4096)


class MemoryRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


@app.before_request
def validate_auth():
    if request.endpoint in PUBLIC_ENDPOINTS or request.method == "OPTIONS":
        return
    key = request.headers.get("X-API-KEY")
    if not key or key != API_KEY:
        logger.warning(f"Unauthorized access attempt: {request.remote_addr}")
        return jsonify({"error": "Unauthorized: Invalid or missing API Key"}), 401


@app.route('/api/v1/chat', methods=['POST'])
@limiter.limit("20 per minute")
def chat_api():
    try:
        data = ChatRequest(**(request.json or {}))
        response = get_ai_response(data.message, role=data.role, history=data.history)
        return jsonify({"status": "success", "response": response})
    except ValidationError as e:
        return jsonify({"status": "error", "errors": e.errors()}), 400
    except Exception as e:
        logger.error(f"Chat API Internal Error: {e}")
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500


@app.route('/api/v1/agent', methods=['POST'])
@limiter.limit("5 per minute")
def agent_api():
    try:
        data = AgentRequest(**(request.json or {}))
        response = run_team_task(data.task, role=data.role)
        return jsonify({"status": "success", "response": response})
    except ValidationError as e:
        return jsonify({"status": "error", "errors": e.errors()}), 400
    except Exception as e:
        logger.error(f"Agent API Internal Error: {e}")
        return jsonify({"status": "error", "message": "Agent execution failed"}), 500


@app.route('/api/v1/image', methods=['POST'])
@limiter.limit("30 per minute")
def image_api():
    try:
        data = ImageRequest(**(request.json or {}))
        url = generate_image(data.prompt, width=data.width, height=data.height)
        return jsonify({"status": "success", "url": url})
    except ValidationError as e:
        return jsonify({"status": "error", "errors": e.errors()}), 400
    except Exception as e:
        logger.error(f"Image API Internal Error: {e}")
        return jsonify({"status": "error", "message": "Image generation failed"}), 500


@app.route('/api/v1/memory', methods=['GET', 'POST'])
@limiter.limit("60 per minute")
def memory_api():
    try:
        if request.method == 'POST':
            data = MemoryRequest(**(request.json or {}))
            result = save_data(data.text)
            return jsonify({"status": "success", "id": result})
        query = request.args.get("q", "").strip()
        if not query:
            return jsonify({"status": "error", "message": "Missing 'q' query parameter"}), 400
        return jsonify({"status": "success", "results": recall_data(query)})
    except ValidationError as e:
        return jsonify({"status": "error", "errors": e.errors()}), 400
    except Exception as e:
        logger.error(f"Memory API Internal Error: {e}")
        return jsonify({"status": "error", "message": "Memory operation failed"}), 500


@app.route('/', methods=['GET'])
def web_index():
    """Serve the built-in web chat UI."""
    return send_from_directory(WEB_DIR, "index.html")


@app.route('/webhook/twilio', methods=['POST'])
@limiter.limit("60 per minute")
def twilio_webhook():
    """WhatsApp via Twilio: receive a message and reply with TwiML."""
    sender, body = whatsapp.parse_twilio(request.form)
    answer = reply_to(body, session_id=f"wa:{sender}") if body else GREETING
    return Response(whatsapp.twiml_reply(answer), mimetype="application/xml")


@app.route('/webhook/whatsapp', methods=['GET', 'POST'])
@limiter.limit("60 per minute")
def whatsapp_webhook():
    """WhatsApp via Meta Cloud API: GET verifies the webhook, POST handles messages."""
    if request.method == 'GET':
        challenge = whatsapp.meta_verify(
            request.args.get("hub.mode"),
            request.args.get("hub.verify_token"),
            request.args.get("hub.challenge"),
        )
        if challenge is not None:
            return Response(challenge, mimetype="text/plain")
        return Response("Verification failed", status=403)

    for sender, text in whatsapp.parse_meta(request.json or {}):
        answer = reply_to(text, session_id=f"wa:{sender}")
        whatsapp.meta_send(sender, answer)
    return jsonify({"status": "received"})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "online",
        "engine": "RAG-MultiAgent-v4",
        "capabilities": ["text", "image", "agent", "rag", "memory"],
        "channels": settings.enabled_channels(),
    })


@app.route('/metrics', methods=['GET'])
def metrics():
    return jsonify({
        "status": "online",
        "env": settings.env,
        "llm_provider": settings.llm_provider,
        "remote_providers": settings.configured_providers(),
        "channels": settings.enabled_channels(),
        "max_iterations": settings.max_iterations,
        "reflection_enabled": settings.enable_reflection,
    })


if __name__ == '__main__':
    logger.info("AI-KU Professional API Server starting...")
    app.run(host=settings.host, port=settings.port, threaded=True)
