from flask import Flask, request, jsonify, render_template
import requests
import urllib.parse

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    if not message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        # Using Pollinations.ai text API
        # Encode message to be safe in URL
        encoded_message = urllib.parse.quote(message)
        # Using a system prompt to ensure it responds well
        system_prompt = urllib.parse.quote("Kamu adalah AI asisten yang pintar dan membantu. Jawablah dalam bahasa Indonesia.")
        url = f"https://text.pollinations.ai/{encoded_message}?system={system_prompt}&model=openai"

        response = requests.get(url)
        if response.status_code == 200:
            # Pollinations might return a notice at the beginning, we might want to filter it if it's always there
            # But usually it's just the response.
            return jsonify({'response': response.text})
        else:
            return jsonify({'error': f'Failed to get response from AI: {response.status_code}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get('prompt', '')
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    # Pollinations.ai image API
    # We return the URL of the generated image
    encoded_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={urllib.parse.quote(str(data.get('seed', '')))}"

    return jsonify({'image_url': image_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
