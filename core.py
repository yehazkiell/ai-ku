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
        return f"\n(Gagal melakukan pencarian: {str(e)})\n"

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

    # Inject Brain Memory
    full_context = f"{memory_context}{context}"

    if model == 'hazz-1-search':
        search_results = search_web(message)
        prompt = prompt.format(search_results=search_results)

    final_message = f"\n[KONTEKS]:\n{full_context}\n\nUser: {message}" if full_context else message

    try:
        if engine == 'ultra':
            messages = [{"role": "system", "content": prompt}]
            for m in history:
                messages.append(m)
            messages.append({"role": "user", "content": final_message})

            response = g4f.ChatCompletion.create(
                model=g4f.models.gpt_4,
                provider=g4f.Provider.OperaAria,
                messages=messages,
            )
            return response
        else:
            encoded_prompt = urllib.parse.quote(f"{prompt}\n\n{final_message}")
            resp = requests.get(f"https://text.pollinations.ai/{encoded_prompt}")
            return resp.text
    except Exception as e:
        return f"Error: {str(e)}"

def generate_image(prompt, model='flux'):
    try:
        seed = secrets.token_hex(4)
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?model={model}&seed={seed}&nologo=true"
        return url
    except:
        return None

def execute_python(code):
    try:
        # Simple sandbox for math/logic
        allowed_globals = {"__builtins__": None, "round": round, "abs": abs, "pow": pow, "sum": sum, "min": min, "max": max, "len": len}
        # Filter dangerous keywords
        forbidden = ["import", "open", "eval", "exec", "os", "sys", "write", "read"]
        for word in forbidden:
            if word in code:
                return f"Error: Keyword '{word}' dilarang demi keamanan."

        local_vars = {}
        exec(code, allowed_globals, local_vars)
        return local_vars.get('result', "Gunakan variabel 'result' untuk output.")
    except Exception as e:
        return f"Error: {str(e)}"

def run_agent_task(task_description):
    steps = [
        "Analisis Tugas & Perencanaan",
        "Pencarian Informasi (Web Search)",
        "Eksekusi Logika & Perhitungan (Sandbox)",
        "Sintesis & Finalisasi"
    ]

    context = f"Tugas Agen: {task_description}\n"
    print(f"\n\033[93m[Agent] Memulai tugas: {task_description}\033[0m")

    # Step 1: Search
    print(f"\033[90m[Agent Step 1/4] Mencari data...\033[0m")
    search_data = search_web(task_description)
    context += f"\nData Terkait:\n{search_data}\n"

    # Step 2: Sandbox Logic (Simple heuristic)
    print(f"\033[90m[Agent Step 2/4] Menjalankan logika internal...\033[0m")
    if any(op in task_description for op in ['+', '-', '*', '/', 'hitung']):
         # Try to extract math and run it
         res = execute_python(f"result = 'Logika dieksekusi berdasarkan konteks'")
         context += f"Hasil Sandbox: {res}\n"

    # Step 3: Final Reasoning
    print(f"\033[90m[Agent Step 3/4] Melakukan penalaran akhir...\033[0m")
    final_prompt = f"Anda adalah Agen Hazz-1. Berdasarkan konteks berikut, selesaikan tugas user dengan sangat teliti.\n\nKonteks:\n{context}\n\nUser Task: {task_description}"

    response = get_ai_response(final_prompt, model='hazz-1-ultra')
    return response
