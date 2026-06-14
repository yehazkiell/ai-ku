import requests
from duckduckgo_search import DDGS
from loguru import logger

def search_web(query, max_results=8):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if not results:
                return "No relevant search results found."

            search_context = "\n🔍 [SUMBER INFORMASI TERVERIFIKASI]:\n"
            for i, r in enumerate(results):
                search_context += f"{i+1}. {r['title']}\n   URL: {r['href']}\n   Snippet: {r['body'][:400]}\n"
            return search_context
    except Exception as e:
        logger.error(f"Search error: {e}")
        return "Gagal melakukan pencarian web."

def fetch_content(url):
    try:
        resp = requests.get(url, timeout=10)
        return resp.text[:5000]
    except Exception as e:
        return f"Error fetching {url}: {e}"
