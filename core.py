import requests
import urllib.parse
import g4f
import secrets
import json
import os
import time
import threading
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

MEMORY_FILE = 'memory.json'
KNOWLEDGE_FILE = 'knowledge.json'

def load_data(file):
    if os.path.exists(file):
        try:
            with open(file, 'r') as f:
                return json.load(f)
        except: return []
    return []

def save_data(file, item):
    data = load_data(file)
    data.append(item)
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

def search_web(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            return "\n".join([f"- {r['title']}: {r['body'][:200]}" for r in results])
    except: return "No data found."

def execute_python(code):
    try:
        local_vars = {}
        exec(code, {"__builtins__": None, "round": round, "abs": abs}, local_vars)
        return local_vars.get('result', "Done")
    except Exception as e: return str(e)

def get_ai_response(message, model='hazz-1-ultra', history=[], context=""):
    system_prompts = {
        'hazz-1-ultra': "Anda adalah Hazz-1 Oracle, AI dengan IQ 300+. Sangat cerdas dan mendalam.",
        'lead': "Anda adalah Lead Orchestrator AI-Ku. Koordinasikan tim untuk hasil terbaik.",
        'researcher': "Anda adalah Peneliti AI-Ku. Cari fakta paling akurat.",
        'coder': "Anda adalah Coder AI-Ku. Tulis kode bersih dan efisien.",
        'analyst': "Anda adalah Analis AI-Ku. Periksa kualitas dan temukan celah."
    }
    prompt = system_prompts.get(model, system_prompts['hazz-1-ultra'])
    full_msg = f"[Context]: {context}\n\nUser: {message}"
    try:
        messages = [{"role": "system", "content": prompt}]
        for m in history: messages.append(m)
        messages.append({"role": "user", "content": full_msg})
        return g4f.ChatCompletion.create(model=g4f.models.gpt_4, provider=g4f.Provider.OperaAria, messages=messages)
    except Exception as e: return f"Error: {e}"

# NEW: AI-Ku Team Orchestration (Claude style)
def run_team_task(task):
    print(f"\n\033[95m[AI-Ku Team] Lead memulai koordinasi...\033[0m")

    # 1. Research
    print(f"\033[90m  -> Researcher sedang bekerja...\033[0m")
    res_data = search_web(task)

    # 2. Analysis
    print(f"\033[90m  -> Analyst sedang memverifikasi...\033[0m")
    analysis = get_ai_response(f"Analisis data ini: {res_data}", model='analyst')

    # 3. Final Construction
    print(f"\033[90m  -> Team Lead menyusun hasil akhir...\033[0m")
    final_output = get_ai_response(f"Tugas: {task}\nData: {res_data}\nAnalisis: {analysis}", model='lead')
    return final_output

# NEW: AI-Ku Scout (Microsoft Scout style - Autonomous Knowledge)
def start_scout_mode():
    def scout_loop():
        while True:
            # Autonomous learning from random trending topics or user interest
            print("\n\033[93m[Scout] Meng-upgrade pengetahuan secara otonom...\033[0m")
            info = search_web("trending tech news and AI advancement 2024")
            save_data(KNOWLEDGE_FILE, f"Observed at {time.ctime()}: {info[:500]}")
            time.sleep(3600) # Every hour

    thread = threading.Thread(target=scout_loop, daemon=True)
    thread.start()

# NEW: Clarification Questions (5-30)
def get_clarifying_questions(task):
    prompt = f"Untuk tugas: '{task}', buatkan 5 pertanyaan klarifikasi singkat agar hasil maksimal. Balas dalam format list 1-5."
    questions = get_ai_response(prompt)
    return questions.strip().split('\n')

def generate_image(prompt, model='flux', style='realistic', ratio='1:1'):
    try:
        styled_prompt = f"{prompt}, style {style}, aspect ratio {ratio}"
        seed = secrets.token_hex(4)
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(styled_prompt)}?model={model}&seed={seed}&nologo=true"
        return url
    except: return None
