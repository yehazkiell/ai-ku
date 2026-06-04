import requests
import urllib.parse
import g4f
import json
import secrets
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

def search_web(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            search_context = "\nHasil Pencarian Terkini:\n"
            for r in results:
                search_context += f"- {r['title']}: {r['body']} (Link: {r['href']})\n"
            return search_context
    except Exception as e:
        return f"\n(Gagal melakukan pencarian: {str(e)})\n"

def get_ai_response(message, model='hazz-1-ultra', engine='ultra', history=[], context=""):
    system_prompts = {
        'hazz-1-ultra': "Anda adalah Hazz-1 Ultra, AI dengan IQ 300+. Berikan jawaban yang sangat cerdas, mendalam, dan teknis.",
        'hazz-1-thinking': "Anda adalah Hazz-1 Thinking. Gunakan tag <thought> untuk proses berpikir sebelum menjawab.",
        'hazz-1-search': "Hazz-1 Search Engine. Gunakan hasil pencarian berikut untuk menjawab: {search_results}",
        'hazz-1-vision': "Hazz-1 Vision. Anda memiliki kemampuan untuk menganalisis dokumen dan gambar melalui teks yang diekstrak. Berikan analisis mendalam."
    }

    prompt = system_prompts.get(model, system_prompts['hazz-1-ultra'])

    full_context = ""
    if context:
        full_context = f"\n[KONTEKS TAMBAHAN/DOKUMEN]:\n{context}\n"

    if model == 'hazz-1-search':
        search_results = search_web(message)
        prompt = prompt.format(search_results=search_results)

    final_message = f"{full_context}{message}"

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
            # Pollinations
            encoded_prompt = urllib.parse.quote(f"{prompt}\n\nUser: {final_message}")
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
