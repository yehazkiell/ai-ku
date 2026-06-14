from loguru import logger


def search_web(query, max_results=5):
    """Web search with source prioritization and citation support.

    ``duckduckgo_search`` is imported lazily so that importing AI-KU does not
    hard-depend on the package being installed.
    """
    try:
        from duckduckgo_search import DDGS
    except Exception as e:
        logger.error(f"duckduckgo_search unavailable: {e}")
        return f"Error: search backend unavailable ({e})."

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if not results:
                return "Verification Failure: No sources found for this query."

            # Prioritize official documentation or wikis when present.
            results.sort(
                key=lambda x: ("docs." in x.get("href", "") or "wiki" in x.get("href", "")),
                reverse=True,
            )

            search_context = "\n🔍 [VERIFIED SOURCES]:\n"
            for i, r in enumerate(results):
                search_context += (
                    f"[{i + 1}] {r.get('title', '')}\n"
                    f"    URL: {r.get('href', '')}\n"
                    f"    PROOF: {r.get('body', '')[:300]}\n"
                )
            search_context += "\n[ACTION]: Cross-verify above results before finalizing response."
            return search_context
    except Exception as e:
        logger.error(f"Search API Error: {str(e)}")
        return f"Error: Web research unavailable. ({str(e)})"
