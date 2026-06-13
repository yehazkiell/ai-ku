from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from core import get_ai_response, run_team_task, generate_image, NEURAL_MATRIX
from dotenv import load_dotenv
import os
import logging
from functools import wraps

load_dotenv()
API_KEY = os.getenv("AIKU_API_KEY")

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AI-KU-ULTRA")

# Increased limits for heavy usage
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10000 per day", "1000 per hour"],
    storage_uri="memory://",
)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("X-API-KEY")
        if not auth or auth != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/v1/chat', methods=['POST'])
@require_auth
def chat_api():
    data = request.json
    response = get_ai_response(data.get('message', ''), role=data.get('role', 'general'))
    return jsonify({"response": response})

@app.route('/api/v1/agent', methods=['POST'])
@require_auth
def agent_api():
    data = request.json
    response = run_team_task(data.get('task', ''))
    return jsonify({"response": response})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ultra-heavy-performance",
        "matrix_size": len(NEURAL_MATRIX),
        "version": "3.0.0-ULTRA"
    })

if __name__ == '__main__':
    # Threaded mode for maximum performance
    app.run(host='0.0.0.0', port=5000, threaded=True)
