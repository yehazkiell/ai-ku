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
    model = data.get('model', 'openai')
    if not message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        # Using Pollinations.ai text API
        encoded_message = urllib.parse.quote(message)
        system_prompt = urllib.parse.quote("Kamu adalah AI asisten yang pintar dan membantu. Jawablah dalam bahasa Indonesia. Gunakan format Markdown untuk jawaban yang panjang atau teknis.")
        url = f"https://text.pollinations.ai/{encoded_message}?system={system_prompt}&model={model}"

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
    model = data.get('model', 'flux') # Default to flux for better quality
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    # Pollinations.ai image API
    encoded_prompt = urllib.parse.quote(prompt)
    width = data.get('width', 1024)
    height = data.get('height', 1024)
    seed = data.get('seed', '')

    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&model={model}&seed={urllib.parse.quote(str(seed))}"

    return jsonify({'image_url': image_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
