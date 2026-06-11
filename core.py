import requests
import urllib.parse
import g4f
import secrets
import json
import os
import time
import threading
import subprocess
from registry import AGENT_REGISTRY
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

MEMORY_FILE = 'memory.json'

def load_data(file):
    if os.path.exists(file):
        try:
            with open(file, 'r') as f: return json.load(f)
        except: return []
    return []

def save_data(file, item):
    data = load_data(file)
    data.append(item)
    with open(file, 'w') as f: json.dump(data, f, indent=4)

def search_web(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            return "\n".join([f"- {r['title']}: {r['body'][:300]}" for r in results])
    except: return "No data found."

def execute_python(code):
    try:
        local_vars = {}
        exec(code, {"__builtins__": None, "round": round, "abs": abs, "pow": pow, "sum": sum, "min": min, "max": max, "len": len}, local_vars)
        return local_vars.get('result', "Execution complete.")
    except Exception as e: return f"Error: {e}"

def get_ai_response(message, role='general', history=[], context=""):
    role_info = AGENT_REGISTRY.get(role, {"prompt": "Anda adalah AI-KU, asisten serba bisa."})
    prompt = role_info['prompt']

    full_msg = f"[Context]: {context}\n\nUser: {message}"
    try:
        messages = [{"role": "system", "content": prompt}]
        for m in history: messages.append(m)
        messages.append({"role": "user", "content": full_msg})
        return g4f.ChatCompletion.create(model=g4f.models.gpt_4, provider=g4f.Provider.OperaAria, messages=messages)
    except Exception as e: return f"Error: {e}"

# AI-KU Forge: Whole-file editing logic (Aider inspired)
def forge_edit_file(filepath, content):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File '{filepath}' berhasil diperbarui."
    except Exception as e: return f"Gagal mengedit file: {e}"

# AI-KU Team Orchestrator
def run_team_task(task):
    print(f"\n\033[95m[AI-KU Forge] Menganalisis proyek...\033[0m")

    # 1. Research & Search
    res_data = search_web(task)

    # 2. Logic & Drafting
    draft = get_ai_response(f"Tugas: {task}\nData Riset: {res_data}", role='coder')

    # 3. Finalization
    return draft

def generate_image(prompt, model='flux'):
    try:
        seed = secrets.token_hex(4)
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?model={model}&seed={seed}&nologo=true"
        return url
    except: return None
