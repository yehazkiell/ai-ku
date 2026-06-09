import requests
import urllib.parse
import g4f
import secrets
import json
import os
import time
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

MEMORY_FILE = 'memory.json'

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        except: return []
    return []

def save_memory(fact):
    memories = load_memory()
    memories.append(fact)
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memories, f, indent=4)

def search_web(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=8)
            search_context = "\n🔍 [SUMBER INFORMASI]:\n"
            for i, r in enumerate(results):
                search_context += f"{i+1}. {r['title']}\n   Desc: {r['body'][:300]}\n   Link: {r['href']}\n"
            return search_context
    except Exception as e:
        return f"\n(Gagal search: {str(e)})\n"

def fetch_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10)
        return resp.text[:5000] # Limit to 5000 chars
    except Exception as e:
        return f"Gagal fetch {url}: {str(e)}"

def execute_python(code):
    try:
        allowed_globals = {"__builtins__": None, "round": round, "abs": abs, "pow": pow, "sum": sum, "min": min, "max": max, "len": len, "list": list, "dict": dict}
        forbidden = ["import", "os", "sys", "write", "read", "eval", "exec"]
        for word in forbidden:
            if word in code:
                return f"Error: Keyword '{word}' dilarang."
        local_vars = {}
        exec(code, allowed_globals, local_vars)
        return local_vars.get('result', "Gunakan variabel 'result' untuk output.")
    except Exception as e:
        return f"Error: {str(e)}"

def get_ai_response(message, model='hazz-1-ultra', engine='ultra', history=[], context=""):
    memories = load_memory()
    memory_context = ""
    if memories:
        memory_context = "\n[MEMORI JANGKA PANJANG]:\n" + "\n".join([f"- {m}" for m in memories[-10:]]) + "\n"

    system_prompts = {
        'hazz-1-ultra': "Anda adalah Hazz-1 Oracle, AI dengan IQ 300+. Refleksi mendalam sebelum menjawab.",
        'hazz-1-thinking': "Anda adalah Hazz-1 Thinking. Gunakan tag <thought>.",
        'hazz-1-search': "Hazz-1 Search Engine. Gunakan hasil pencarian: {search_results}",
        'hazz-1-vision': "Hazz-1 Vision. Analisis dokumen/gambar."
    }

    prompt = system_prompts.get(model, system_prompts['hazz-1-ultra'])
    full_context_final = f"{memory_context}{context}"

    if model == 'hazz-1-search':
        search_results = search_web(message)
        prompt = prompt.format(search_results=search_results)

    final_message = f"\n[KONTEKS]:\n{full_context_final}\n\nUser: {message}" if full_context_final else message

    try:
        if engine == 'ultra':
            messages = [{"role": "system", "content": prompt}]
            for m in history: messages.append(m)
            messages.append({"role": "user", "content": final_message})
            response = g4f.ChatCompletion.create(model=g4f.models.gpt_4, provider=g4f.Provider.OperaAria, messages=messages)
            return response
        else:
            encoded_prompt = urllib.parse.quote(f"{prompt}\n\n{final_message}")
            resp = requests.get(f"https://text.pollinations.ai/{encoded_prompt}")
            return resp.text
    except Exception as e:
        return f"Error: {str(e)}"

def run_agent_task(task_description, role='general'):
    print(f"\n\033[93m[Agent ReAct] Role: {role.upper()} | Task: {task_description}\033[0m")
    agent_context = f"Role: {role}. Task: {task_description}\n"

    # ReAct Loop (Max 3 iterations)
    for i in range(3):
        print(f"\033[90m[Loop {i+1}/3] Berpikir & Mengambil tindakan...\033[0m")

        # Determine next action
        think_prompt = f"Anda adalah Agen Otonom. Tugas: {task_description}.\nKonteks saat ini: {agent_context}\n\nApa tindakan Anda selanjutnya? Pilih satu:\n1. SEARCH [query]\n2. FETCH [url]\n3. RUN [python_code]\n4. FINISH\n\nBalas hanya dengan format: ACTION: [PILIHAN] ARGS: [ARGUMEN]"
        action_decision = get_ai_response(think_prompt, model='hazz-1-ultra')

        if "FINISH" in action_decision:
            break

        if "SEARCH" in action_decision:
            query = action_decision.split("ARGS:")[1].strip()
            print(f"  -> Action: Searching for '{query}'")
            res = search_web(query)
            agent_context += f"\nSearch Result: {res[:1000]}\n"
        elif "FETCH" in action_decision:
            url = action_decision.split("ARGS:")[1].strip()
            print(f"  -> Action: Fetching {url}")
            res = fetch_url(url)
            agent_context += f"\nURL Content: {res[:1000]}\n"
        elif "RUN" in action_decision:
            code = action_decision.split("ARGS:")[1].strip()
            print(f"  -> Action: Running Python Logic")
            res = execute_python(code)
            agent_context += f"\nExecution Result: {res}\n"

    print("\033[90m[Finalizing] Menyusun jawaban akhir...\033[0m")
    final_prompt = f"Berdasarkan investigasi Anda: {agent_context}\n\nBerikan jawaban final untuk tugas: {task_description}"
    return get_ai_response(final_prompt, model='hazz-1-ultra')

def generate_image(prompt, model='flux', style='realistic', ratio='1:1'):
    try:
        styled_prompt = f"{prompt}, style {style}, aspect ratio {ratio}"
        seed = secrets.token_hex(4)
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(styled_prompt)}?model={model}&seed={seed}&nologo=true"
        return url
    except: return None
