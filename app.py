from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from core import get_ai_response, generate_image, run_team_task
from dotenv import load_dotenv
import os
import logging
from functools import wraps

# Load configuration
load_dotenv()
API_KEY = os.getenv("AIKU_API_KEY")

app = Flask(__name__)

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AI-KU")

# Rate Limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("X-API-KEY")
        if not auth or auth != API_KEY:
            logger.warning(f"Unauthorized access attempt from {request.remote_addr}")
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/v1/chat', methods=['POST'])
@limiter.limit("10 per minute")
@require_auth
def chat_api():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Missing 'message'"}), 400

    # Input size limit
    if len(data['message']) > 2000:
        return jsonify({"error": "Input too long (max 2000 chars)"}), 400

    response = get_ai_response(data['message'], role=data.get('role', 'general'))
    return jsonify({"response": response})

@app.route('/api/v1/agent', methods=['POST'])
@require_auth
def agent_api():
    data = request.json
    if not data or 'task' not in data:
        return jsonify({"error": "Missing 'task'"}), 400

    response = run_team_task(data['task'])
    return jsonify({"response": response})

@app.route('/api/v1/generate-image', methods=['POST'])
@require_auth
def image_api():
    data = request.json
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing 'prompt'"}), 400

    url = generate_image(data['prompt'])
    return jsonify({"url": url})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "version": "2.1.0"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
