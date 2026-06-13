MODEL_MATRIX = {
    "CHAT": {
        "ai-ku-core-mini": {"tokens": "128K", "desc": "Fast & Efficient chat."},
        "ai-ku-core-pro": {"tokens": "2M", "desc": "Deep reasoning and logic."},
        "ai-ku-core-max": {"tokens": "10M", "desc": "Massive context analysis."}
    },
    "IMAGE": {
        "ai-ku-pixel-fast": {"res": "512x512", "desc": "Instant generation."},
        "ai-ku-pixel-studio": {"res": "1024x1024", "desc": "High-fidelity studio art."},
        "ai-ku-pixel-ultra": {"res": "4K Ultra", "desc": "Hyper-realistic rendering."}
    },
    "CODING": {
        "ai-ku-forge-lite": {"power": "Basic", "desc": "Bug fixing and scripts."},
        "ai-ku-forge-titan": {"power": "Extreme", "desc": "Whole project refactoring."}
    },
    "SEARCH": {
        "ai-ku-scout-lite": {"depth": "Shallow", "desc": "Quick news & facts."},
        "ai-ku-scout-deep": {"depth": "Medium", "desc": "In-depth technical research."},
        "ai-ku-scout-oracle": {"depth": "Infinity", "desc": "Cross-dimensional data mining."}
    },
    "HYBRID (OMNI)": {
        "ai-ku-omni-basic": {"tokens": "5M", "desc": "All-in-one entry level."},
        "ai-ku-omni-advanced": {"tokens": "25M", "desc": "Pro-grade multi-tasking."},
        "ai-ku-omni-prime": {"tokens": "50M", "desc": "Enterprise orchestrator."},
        "ai-ku-omni-godmode": {"tokens": "100M+", "desc": "Infinite context & zero-shot mastery."}
    }
}

AGENT_REGISTRY = {
    "lead": {"prompt": "AI-KU Godmode Lead. Orchestrate the matrix."},
    "coder": {"prompt": "AI-KU Forge Master. Architecture and implementation."},
    "researcher": {"prompt": "AI-KU Scout Oracle. Information retrieval."},
    "analyst": {"prompt": "AI-KU Logic Core. Verification and reflection."}
}
