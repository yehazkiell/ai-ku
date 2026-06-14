from aiku.agents.orchestrator import orchestrator
from aiku.memory.rag import memory_instance
from aiku.tools.search import search_web
from aiku.tools.sandbox import execute_python
import secrets
import urllib.parse
import threading
import time

def get_ai_response(message, role='general', history=[], context=""):
    full_prompt = f"{context}\\n\\nUser: {message}"
    return orchestrator.call_llm(full_prompt, role=role, history=history)

def run_team_task(task):
    return orchestrator.run_multi_agent_task(task)

def save_data(item):
    memory_instance.add_memory(item)

def generate_image(prompt):
    seed = secrets.token_hex(4)
    return f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?seed={seed}&nologo=true"

def start_scout_mode():
    def scout_loop():
        while True:
            # Smart browsing
            info = search_web("Lates AI breakthroughs and Open Source models")
            memory_instance.add_memory(f"Autonomous knowledge update: {info[:500]}", metadata={"source": "scout"})
            time.sleep(7200) # Every 2 hours
    threading.Thread(target=scout_loop, daemon=True).start()

def get_clarifying_questions(task):
    prompt = f"TASK: '{task}'. Generate 5 critical clarifying questions to ensure perfect execution."
    res = get_ai_response(prompt, role="analyst")
    return [q.strip() for q in res.split('\\n') if q.strip()]
