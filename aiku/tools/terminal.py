import subprocess
from loguru import logger

def run_command(command):
    """Executes a terminal command safely and returns the output."""
    logger.info(f"Terminal execution: {command}")
    # List of dangerous commands to block as a basic safeguard
    dangerous = ["rm -rf /", "mkfs", ":(){ :|:& };:", "dd if=/dev/zero"]
    if any(d in command for d in dangerous):
        return "Error: Command blocked for safety."

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return output if output else "Command executed with no output."
    except subprocess.TimeoutExpired:
        return "Error: Command timed out."
    except Exception as e:
        return f"Error: {str(e)}"
