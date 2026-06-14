import os
from loguru import logger

def write_file(filepath, content):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error writing file: {e}"

def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def list_project_files(startpath='.'):
    file_list = []
    for root, dirs, files in os.walk(startpath):
        if '.git' in dirs: dirs.remove('.git')
        if '__pycache__' in dirs: dirs.remove('__pycache__')
        for f in files:
            file_list.append(os.path.join(root, f))
    return file_list

def list_project_files(path='.'):
    """Secure file listing."""
    files = []
    for root, _, filenames in os.walk(path):
        if 'chroma_db' in root or '.git' in root or '__pycache__' in root:
            continue
        for f in filenames:
            files.append(os.path.join(root, f))
    return files[:50] # Hard limit for context safety
