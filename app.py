from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
from core import get_ai_response, run_team_task, generate_image
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("AIKU_API_KEY", "aiku_master_key_123")

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

@app.before_request
def validate_auth():
    if request.endpoint == 'health' or request.method == 'OPTIONS':
        return
    key = request.headers.get("X-API-KEY")
    if not key or key != API_KEY:
        logger.warning(f"Unauthorized access attempt: {request.remote_addr}")
        return jsonify({"error": "Unauthorized: Invalid or missing API Key"}), 401

@app.route('/api/v1/chat', methods=['POST'])
@limiter.limit("20 per minute")
def chat_api():
    try:
        data = ChatRequest(**request.json)
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
        data = AgentRequest(**request.json)
        response = run_team_task(data.task)
        return jsonify({"status": "success", "response": response})
    except ValidationError as e:
        return jsonify({"status": "error", "errors": e.errors()}), 400
    except Exception as e:
        logger.error(f"Agent API Internal Error: {e}")
        return jsonify({"status": "error", "message": "Agent execution failed"}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "online",
        "engine": "RAG-MultiAgent-v4",
        "capabilities": ["text", "image", "agent", "rag"]
    })

if __name__ == '__main__':
    # Production-ready Flask server with logger integration
    logger.info("AI-KU Professional API Server starting...")
    app.run(host='0.0.0.0', port=5000, threaded=True)
