import os
from loguru import logger

# Directories that should never be walked or returned to the agent.
_EXCLUDED_DIRS = {".git", "__pycache__", "chroma_db", ".venv", "node_modules"}


def write_file(filepath, content):
    """Write text to ``filepath``, creating parent directories when needed."""
    try:
        parent = os.path.dirname(filepath)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        logger.error(f"write_file error for {filepath}: {e}")
        return f"Error writing file: {e}"


def read_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"read_file error for {filepath}: {e}")
        return f"Error reading file: {e}"


def list_project_files(path=".", limit=50):
    """List project files, skipping noise directories. Hard-limited for context safety."""
    files = []
    for root, dirs, filenames in os.walk(path):
        # prune excluded dirs in-place so os.walk doesn't descend into them
        dirs[:] = [d for d in dirs if d not in _EXCLUDED_DIRS]
        for f in filenames:
            files.append(os.path.join(root, f))
            if len(files) >= limit:
                return files
    return files
