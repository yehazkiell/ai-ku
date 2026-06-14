from aiku.agents.orchestrator import orchestrator
from aiku.memory.rag import memory_instance
from aiku.tools.search import search_web
from aiku.tools.sandbox import execute_python
import secrets
import urllib.parse
import threading
import time

def get_ai_response(message, role='general', history=[], context=""):
    return orchestrator.call_llm(message)

def run_team_task(task):
    return orchestrator.run_task(task)

def save_data(item):
    memory_instance.add_memory(item)

def generate_image(prompt):
    seed = secrets.token_hex(4)
    return f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?seed={seed}&nologo=true"

def start_scout_mode():
    def scout_loop():
        while True:
            info = search_web("Latest AI news")
            memory_instance.add_memory(f"Knowledge update: {info[:500]}")
            time.sleep(7200)
    threading.Thread(target=scout_loop, daemon=True).start()
