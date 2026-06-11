import requests
import urllib.parse
import g4f
import secrets
import json
import os
import time
import logging
from filelock import FileLock
from registry import AGENT_REGISTRY
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("AI-KU-CORE")

MEMORY_FILE = 'memory.json'
LOCK_FILE = 'memory.lock'

def load_data():
    if not os.path.exists(MEMORY_FILE): return []
    with FileLock(LOCK_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f: return json.load(f)
        except: return []

def save_data(item):
    data = load_data()
    data.append({"timestamp": time.time(), "content": item})
    # Keep memory efficient (last 50 items)
    data = data[-50:]
    with FileLock(LOCK_FILE):
        with open(MEMORY_FILE, 'w') as f: json.dump(data, f, indent=4)

def search_web(query):
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            search_context = "\n🔍 [SOURCES]:\n"
            for i, r in enumerate(results):
                search_context += f"{i+1}. {r['title']}\n   URL: {r['href']}\n   Snippet: {r['body'][:200]}\n"
            return search_context
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return "Search unavailable."

def execute_python(code):
    """Secure sandbox for logical operations."""
    if len(code) > 500: return "Error: Code too long."
    forbidden = ["import", "os", "sys", "open", "eval", "exec", "subprocess", "__", "write"]
    if any(word in code.lower() for word in forbidden):
        return "Error: Security violation detected."

    try:
        local_vars = {}
        exec(code, {"__builtins__": None, "round": round, "abs": abs, "len": len}, local_vars)
        return local_vars.get('result', "Success")
    except Exception as e: return f"Execution error: {e}"

def get_ai_response(message, role='general', history=[], context=""):
    role_info = AGENT_REGISTRY.get(role, AGENT_REGISTRY['coder'])
    prompt = role_info['prompt']

    # Provider Fallback System
    providers = [
        (g4f.Provider.OperaAria, g4f.models.gpt_4),
        (g4f.Provider.Blackbox, g4f.models.gpt_4),
    ]

    full_msg = f"[Context]: {context}\n\nUser: {message}"
    messages = [{"role": "system", "content": prompt}]
    for m in history: messages.append(m)
    messages.append({"role": "user", "content": full_msg})

    for provider, model in providers:
        try:
            logger.info(f"Attempting response with {provider.__name__}")
            return g4f.ChatCompletion.create(model=model, provider=provider, messages=messages)
        except Exception as e:
            logger.warning(f"Provider {provider.__name__} failed: {e}")
            continue

    # Final Fallback to Pollinations
    try:
        logger.info("Falling back to Pollinations API")
        encoded = urllib.parse.quote(f"{prompt}\n\n{full_msg}")
        return requests.get(f"https://text.pollinations.ai/{encoded}").text
    except:
        return "Error: All AI providers failed."

def run_team_task(task):
    logger.info(f"Running team task: {task}")
    res_data = search_web(task)
    return get_ai_response(f"Tugas: {task}\nData: {res_data}", role='coder')

def generate_image(prompt):
    try:
        seed = secrets.token_hex(4)
        return f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?seed={seed}&nologo=true"
    except: return None
