import sys
from loguru import logger

def execute_python(code):
    """Hardened sandbox for logic execution."""
    if len(code) > 2000: return "Error: Code too long."

    # Keyword filtering
    forbidden = ["import", "os", "sys", "open", "eval", "exec", "subprocess", "__", "write", "socket"]
    if any(word in code.lower() for word in forbidden):
        return "Error: Security violation detected (Forbidden keywords)."

    try:
        # Restricted globals
        allowed_globals = {
            "__builtins__": None,
            "round": round, "abs": abs, "len": len,
            "sum": sum, "max": max, "min": min,
            "list": list, "dict": dict, "str": str, "int": int, "float": float
        }
        local_vars = {}
        exec(code, allowed_globals, local_vars)
        return local_vars.get('result', "Execution complete (Remember to use 'result' variable for output).")
    except Exception as e:
        logger.error(f"Sandbox error: {e}")
        return f"Execution error: {e}"
