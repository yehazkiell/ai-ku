from flask import Flask, request, jsonify, render_template
import requests
import urllib.parse
import g4f
import json
import PyPDF2
import io
from werkzeug.utils import secure_filename
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
import secrets
import os
from functools import wraps

app = Flask(__name__)

KEYS_FILE = 'keys.json'

def load_keys():
    if not os.path.exists(KEYS_FILE):
        return {}
    try:
        with open(KEYS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f)

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        api_key = None
        if auth_header and auth_header.startswith('Bearer '):
            api_key = auth_header.split(' ')[1]

        keys = load_keys()
        if not api_key or api_key not in keys:
            return jsonify({'error': 'Unauthorized: Invalid or missing API Key'}), 401
        return f(*args, **kwargs)
    return decorated


def extract_text_from_file(file):
    filename = secure_filename(file.filename)
    if filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif filename.endswith(('.txt', '.md', '.py', '.js', '.html', '.css')):
        return file.read().decode('utf-8')
    return ""

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        text = extract_text_from_file(file)
        return jsonify({"text": text, "filename": file.filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-title', methods=['POST'])
def generate_title():
    data = request.json
    message = data.get('message', '')
    if not message:
        return jsonify({"title": "Chat Baru"})

    try:
        prompt = f"Berikan judul singkat (maks 3-5 kata) untuk percakapan yang dimulai dengan pesan ini: '{message}'. Balas HANYA dengan judulnya saja tanpa tanda kutip."
        response = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}?model=openai")
        title = response.text.strip().replace('"', '')
        return jsonify({"title": title})
    except:
        return jsonify({"title": "Chat Terpilih"})

@app.route('/')
def index():
    return render_template('index.html')

def search_web(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            search_context = "\nHasil Pencarian Terkini:\n"
            for r in results:
                search_context += f"- {r['title']}: {r['body']} (Link: {r['href']})\n"
            return search_context
    except Exception as e:
        print(f"Search error: {e}")
        return ""

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    model = data.get('model', 'openai')
    engine = data.get('engine', 'pollination')
    custom_system = data.get('system_prompt', "Kamu adalah AI asisten yang pintar dan membantu. Jawablah dalam bahasa Indonesia. Gunakan format Markdown untuk jawaban yang panjang atau teknis.")
    learning_content = data.get('learning_content', '')

    if not message:
        return jsonify({'error': 'No message provided'}), 400

    # Hazz Model Logic
    if model.startswith('hazz-'):
        engine = 'ultra' # Force ultra engine for Hazz models
        if model == 'hazz-1-thinking':
            custom_system = "Kamu adalah Hazz-1 Thinking. Sebelum menjawab, kamu HARUS berpikir secara mendalam dalam blok <thought>. Analisis masalah langkah demi langkah, pertimbangkan berbagai perspektif, lalu berikan jawaban final yang sangat akurat."
        elif model == 'hazz-1-search' or model == 'hazz-1-vision':
            search_data = search_web(message)
            message = f"{search_data}\n\nBerdasarkan data di atas, jawab pertanyaan ini: {message}"
            custom_system = "Kamu adalah Hazz-1 Search. Gunakan hasil pencarian yang diberikan untuk memberikan jawaban yang paling update dan faktual."
        elif model == 'hazz-1-ultra':
            custom_system = "Kamu adalah Hazz-1 Ultra, model AI paling cerdas dengan IQ 300+. Berikan jawaban yang sangat jenius, filosofis, dan teknis jika diperlukan."

    if learning_content:
        message = f"Konteks Pembelajaran: {learning_content}\n\nPertanyaan: {message}"

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

@app.route('/developer/keys', methods=['GET'])
def get_user_keys():
    return jsonify(load_keys())

from datetime import datetime

@app.route('/developer/keys/generate', methods=['POST'])
def generate_key():
    data = request.json
    name = data.get('name', 'Default Key')
    new_key = f"ai_ku_{secrets.token_hex(16)}"
    keys = load_keys()
    keys[new_key] = {
        'name': name,
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_keys(keys)
    return jsonify({'key': new_key, 'name': name})

@app.route('/developer/keys/revoke', methods=['POST'])
def revoke_key():
    data = request.json
    key_to_revoke = data.get('key')
    keys = load_keys()
    if key_to_revoke in keys:
        del keys[key_to_revoke]
        save_keys(keys)
        return jsonify({'success': True})
    return jsonify({'error': 'Key not found'}), 404

# External API V1
@app.route('/api/v1/chat', methods=['POST'])
@require_api_key
def api_chat():
    return chat()

@app.route('/api/v1/generate-image', methods=['POST'])
@require_api_key
def api_generate_image():
    return generate_image()

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
