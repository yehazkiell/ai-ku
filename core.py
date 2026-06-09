import requests
import urllib.parse
import g4f
import secrets
import json
import os
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
            search_context = "\n🔍 [SUMBER INFORMASI TERVALIDASI]:\n"
            for i, r in enumerate(results):
                search_context += f"{i+1}. {r['title']}\n   Deskripsi: {r['body'][:300]}\n   Link: {r['href']}\n"
            search_context += "\n[TUGAS]: Rangkum informasi di atas untuk menjawab pertanyaan user dengan akurat.\n"
            return search_context
    except Exception as e:
        return f"\n(Pencarian terbatas: {str(e)})\n"

def execute_python(code):
    try:
        allowed_globals = {"__builtins__": None, "round": round, "abs": abs, "pow": pow, "sum": sum, "min": min, "max": max, "len": len}
        forbidden = ["import", "open", "eval", "exec", "os", "sys", "write", "read"]
        for word in forbidden:
            if word in code:
                return f"Error: Keyword '{word}' dilarang demi keamanan."
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
        'hazz-1-ultra': "Anda adalah Hazz-1 Oracle, AI dengan IQ 300+. Sebelum menjawab, lakukan refleksi internal untuk memastikan akurasi 100%.",
        'hazz-1-thinking': "Anda adalah Hazz-1 Thinking. Gunakan tag <thought> untuk proses berpikir sebelum menjawab.",
        'hazz-1-search': "Hazz-1 Search Engine. Gunakan hasil pencarian berikut untuk menjawab: {search_results}",
        'hazz-1-vision': "Hazz-1 Vision. Analisis dokumen/gambar melalui teks yang diekstrak."
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
            for m in history:
                messages.append(m)
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
    roles = {
        'researcher': "Spesialis riset mendalam.",
        'coder': "Spesialis pemrograman.",
        'architect': "Spesialis desain sistem.",
        'writer': "Spesialis konten.",
        'general': "Agen serba bisa."
    }
    role_desc = roles.get(role, roles['general'])
    print(f"\n\033[93m[Agent Arena] Role: {role.upper()} | Task: {task_description}\033[0m")

    print("\033[90m[Step 1/3] Meriset data...\033[0m")
    search_data = search_web(f"{role} context for {task_description}")

    print("\033[90m[Step 2/3] Menyimpan workspace...\033[0m")
    try:
        with open('agent_workspace.txt', 'w') as f:
            f.write(f"Task: {task_description}\nRole: {role}\nData: {search_data}")
    except: pass

    print("\033[90m[Step 3/3] Finalisasi...\033[0m")
    final_prompt = f"Anda Agen Hazz Role {role_desc}. Data Riset: {search_data}. Tugas: {task_description}"
    return get_ai_response(final_prompt, model='hazz-1-ultra')

def generate_image(prompt, model='flux'):
    try:
        seed = secrets.token_hex(4)
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?model={model}&seed={seed}&nologo=true"
        return url
    except: return None
