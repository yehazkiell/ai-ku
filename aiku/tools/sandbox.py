"""A small, safer Python expression/logic sandbox.

Validation is AST-based rather than substring-based, so legitimate code like
``cost = position * 2`` is no longer wrongly rejected (the old denylist matched
the substring "os" inside such names), while imports, attribute access to dunder
internals, and dangerous builtins are reliably blocked.

This is intended for arithmetic / data-shaping logic, not as a hard security
boundary against a determined adversary.
"""
import ast
import math

from loguru import logger

_MAX_CODE_LEN = 2000

# Builtins that could break out of the sandbox or touch the host.
_FORBIDDEN_NAMES = {
    "eval", "exec", "open", "compile", "__import__", "input",
    "globals", "locals", "vars", "getattr", "setattr", "delattr",
    "exit", "quit", "help", "breakpoint", "memoryview", "object",
}

# A curated, safe set of builtins exposed to the executed code.
_SAFE_BUILTINS = {
    "abs": abs, "round": round, "min": min, "max": max, "sum": sum,
    "len": len, "sorted": sorted, "reversed": reversed, "range": range,
    "enumerate": enumerate, "zip": zip, "map": map, "filter": filter,
    "any": any, "all": all, "pow": pow, "divmod": divmod, "bool": bool,
    "int": int, "float": float, "str": str, "list": list, "dict": dict,
    "set": set, "tuple": tuple, "frozenset": frozenset, "print": print,
}


def _validate(tree):
    """Return a human-readable reason if ``tree`` is unsafe, else ``None``."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return "imports are not allowed"
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            return "access to dunder attributes is not allowed"
        if isinstance(node, ast.Name):
            if node.id.startswith("__"):
                return "access to dunder names is not allowed"
            if node.id in _FORBIDDEN_NAMES:
                return f"use of '{node.id}' is not allowed"
    return None


def execute_python(code):
    """Run a short snippet and return its ``result`` variable (or a message)."""
    if not code or not code.strip():
        return "Error: empty code."
    if len(code) > _MAX_CODE_LEN:
        return "Error: Code too long."

    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as e:
        return f"Error: invalid syntax ({e})."

    reason = _validate(tree)
    if reason:
        return f"Error: Security violation detected ({reason})."

    try:
        allowed_globals = {"__builtins__": _SAFE_BUILTINS, "math": math}
        local_vars = {}
        exec(compile(tree, "<sandbox>", "exec"), allowed_globals, local_vars)
        return local_vars.get(
            "result",
            "Execution complete (set the 'result' variable to return a value).",
        )
    except Exception as e:
        logger.error(f"Sandbox error: {e}")
        return f"Execution error: {e}"
