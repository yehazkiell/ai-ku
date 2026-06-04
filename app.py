from flask import Flask, request, jsonify, render_template
import requests
import urllib.parse
import g4f

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    model = data.get('model', 'openai')
    engine = data.get('engine', 'pollination') # pollination or ultra
    custom_system = data.get('system_prompt', "Kamu adalah AI asisten yang pintar dan membantu. Jawablah dalam bahasa Indonesia. Gunakan format Markdown untuk jawaban yang panjang atau teknis.")

    if not message:
        return jsonify({'error': 'No message provided'}), 400

    if engine == 'ultra':
        try:
            # Using g4f with OperaAria (verified working)
            response = g4f.ChatCompletion.create(
                model="gpt-4",
                provider=g4f.Provider.OperaAria,
                messages=[
                    {"role": "system", "content": custom_system},
                    {"role": "user", "content": message}
                ],
            )
            return jsonify({'response': response})
        except Exception as e:
            # Fallback to pollination if ultra fails
            print(f"Ultra engine error: {e}, falling back...")
            engine = 'pollination'

    try:
        # Using Pollinations.ai text API
        encoded_message = urllib.parse.quote(message)
        encoded_system = urllib.parse.quote(custom_system)
        url = f"https://text.pollinations.ai/{encoded_message}?system={encoded_system}&model={model}"

        response = requests.get(url)
        if response.status_code == 200:
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
