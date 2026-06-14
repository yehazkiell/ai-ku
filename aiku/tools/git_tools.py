import os
import subprocess
from loguru import logger

def git_status():
    try:
        res = subprocess.run(["git", "status"], capture_output=True, text=True)
        return res.stdout
    except: return "Not a git repository or git not installed."

def git_log(n=5):
    try:
        res = subprocess.run(["git", "log", f"-n {n}", "--oneline"], capture_output=True, text=True)
        return res.stdout
    except: return "Error retrieving git log."
