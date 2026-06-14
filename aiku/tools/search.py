import requests
from duckduckgo_search import DDGS
from loguru import logger

def search_web(query, max_results=5):
    """
    Enhanced search with source prioritization and citation support.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if not results:
                return "Verification Failure: No sources found for this query."

            # Simple ranking: prioritze official documentation or wikis if keywords match
            results.sort(key=lambda x: ('docs.' in x['href'] or 'wiki' in x['href']), reverse=True)

            search_context = "\n🔍 [VERIFIED SOURCES]:\n"
            for i, r in enumerate(results):
                search_context += f"[{i+1}] {r['title']}\n    URL: {r['href']}\n    PROOF: {r['body'][:300]}\n"

            search_context += "\n[ACTION]: Cross-verify above results before finalizing response."
            return search_context
    except Exception as e:
        logger.error(f"Search API Error: {str(e)}")
        return f"Error: Web research unavailable. ({str(e)})"
