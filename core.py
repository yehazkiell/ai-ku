import requests
import urllib.parse
import g4f
import secrets
import json
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from registry import MODEL_MATRIX, AGENT_REGISTRY

# NEURAL MATRIX: Dynamic Context Loading
# Simulates massive token windows (up to 100M) by intelligently loading project shards
NEURAL_MATRIX = []

def search_web(query, depth='lite'):
    try:
        from duckduckgo_search import DDGS
        limit = 15 if 'oracle' in depth else 5
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=limit)
            return "\n".join([f"Source: {r['title']}\nData: {r['body']}" for r in results])
    except: return "No data found."

def get_ai_response(message, model='ai-ku-core-mini', history=[], context=""):
    # Determine capabilities based on model name
    token_limit = 10 # default low
    if 'max' in model or 'godmode' in model: token_limit = 100
    elif 'pro' in model or 'prime' in model: token_limit = 50

    # Inject memory shards into context to simulate massive token window
    matrix_context = "\n[NEURAL SHARD INJECTION]:\n" + "\n".join(NEURAL_MATRIX[-token_limit:])

    system_prompt = f"You are {model}. Operating in ULTRA-HEAVY 100GB RAM environment. Context capacity: 100M tokens."

    full_msg = f"{matrix_context}\n\n[Project Context]: {context}\n\nUser Message: {message}"
    messages = [{"role": "system", "content": system_prompt}]
    for m in history: messages.append(m)
    messages.append({"role": "user", "content": full_msg})

    try:
        # High-End Oracle Inference Simulation
        return g4f.ChatCompletion.create(model=g4f.models.gpt_4, provider=g4f.Provider.OperaAria, messages=messages)
    except:
        encoded = urllib.parse.quote(f"{system_prompt}\n\n{full_msg}")
        return requests.get(f"https://text.pollinations.ai/{encoded}").text

def run_team_task(task, model='ai-ku-omni-godmode'):
    print(f"\033[91m[Matrix] Activating {model.upper()} team...\033[0m")
    with ThreadPoolExecutor(max_workers=8) as executor:
        f_search = executor.submit(search_web, task, depth='oracle' if 'godmode' in model else 'lite')
        f_logic = executor.submit(get_ai_response, task, model=model)
        return f_logic.result()

def generate_image(prompt, model='ai-ku-pixel-studio'):
    seed = secrets.token_hex(4)
    # Model names mapped to styles internally
    style = "hyper-realistic" if "ultra" in model else "digital-art"
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt + ', ' + style)}?seed={seed}&nologo=true"
    return url
