import os
from loguru import logger

from aiku.config import settings

# Directories that should never be walked or returned to the agent.
_EXCLUDED_DIRS = {".git", "__pycache__", "chroma_db", ".venv", "node_modules"}


def _workspace_root():
    """Absolute root that all file operations are confined to (per call)."""
    return os.path.realpath(settings.workspace_dir or os.getcwd())


def _safe_path(filepath):
    """Resolve ``filepath`` and guarantee it stays inside the workspace root.

    Blocks ``..`` traversal, absolute paths outside the workspace, and symlink
    escapes (via ``realpath``). Raises ``ValueError`` when the path escapes.
    """
    root = _workspace_root()
    candidate = filepath if os.path.isabs(filepath) else os.path.join(root, filepath)
    real = os.path.realpath(candidate)
    if real != root and not real.startswith(root + os.sep):
        raise ValueError(f"Access denied: '{filepath}' is outside the workspace.")
    return real


def write_file(filepath, content):
    """Write text to ``filepath`` (inside the workspace), creating parents."""
    try:
        target = _safe_path(filepath)
    except ValueError as e:
        logger.warning(f"write_file blocked: {e}")
        return f"Error: {e}"
    try:
        parent = os.path.dirname(target)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        logger.error(f"write_file error for {filepath}: {e}")
        return f"Error writing file: {e}"


def read_file(filepath):
    """Read text from ``filepath`` (inside the workspace), capped in size."""
    try:
        target = _safe_path(filepath)
    except ValueError as e:
        logger.warning(f"read_file blocked: {e}")
        return f"Error: {e}"
    try:
        limit = settings.max_file_read_bytes
        with open(target, "r", encoding="utf-8") as f:
            data = f.read(limit + 1)
        if len(data) > limit:
            return data[:limit] + f"\n\n[...truncated at {limit} bytes...]"
        return data
    except Exception as e:
        logger.error(f"read_file error for {filepath}: {e}")
        return f"Error reading file: {e}"


def list_project_files(path=".", limit=50):
    """List project files, skipping noise directories. Hard-limited for context safety."""
    try:
        root = _safe_path(path)
    except ValueError as e:
        logger.warning(f"list_project_files blocked: {e}")
        return [f"Error: {e}"]
    files = []
    for cur, dirs, filenames in os.walk(root):
        # prune excluded dirs in-place so os.walk doesn't descend into them
        dirs[:] = [d for d in dirs if d not in _EXCLUDED_DIRS]
        for f in filenames:
            files.append(os.path.relpath(os.path.join(cur, f), root))
            if len(files) >= limit:
                return files
    return files
