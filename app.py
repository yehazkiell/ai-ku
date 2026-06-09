from flask import Flask, request, jsonify
from core import get_ai_response, generate_image
import json
import os

app = Flask(__name__)

@app.route('/api/v1/chat', methods=['POST'])
def chat_api():
    data = request.json
    message = data.get('message')
    model = data.get('model', 'hazz-1-ultra')
    engine = data.get('engine', 'ultra')
    history = data.get('history', [])
    context = data.get('context', '')

    if not message:
        return jsonify({"error": "Message is required"}), 400

    response = get_ai_response(message, model=model, engine=engine, history=history, context=context)
    return jsonify({"response": response})

@app.route('/api/v1/generate-image', methods=['POST'])
def image_api():
    data = request.json
    prompt = data.get('prompt')
    model = data.get('model', 'flux')

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    url = generate_image(prompt, model=model)
    return jsonify({"url": url})


@app.route('/api/v1/agent', methods=['POST'])
def agent_api():
    data = request.json
    task = data.get('task')
    role = data.get('role', 'general')
    if not task:
        return jsonify({"error": "Task is required"}), 400

    from core import run_agent_task
    response = run_agent_task(task, role=role)
    return jsonify({"response": response})

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "online", "message": "Hazz-1 API is running with low RAM footprint (approx 200MB)"})

if __name__ == '__main__':
    # Running on 0.0.0.0 to be accessible for bot integrations
    app.run(host='0.0.0.0', port=5000)
