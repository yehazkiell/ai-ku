import re
import subprocess

from loguru import logger

from aiku.config import settings

# Patterns for clearly destructive / dangerous commands. A denylist is not a
# security boundary on its own (use AIKU_ALLOW_SHELL=false or a container for
# untrusted input), but it stops the most common foot-guns.
_DANGEROUS_PATTERNS = [
    r"\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r",  # rm -rf / -fr (any order)
    r"\bmkfs\b",                                        # format a filesystem
    r"\bdd\b[^\n]*\bof=/dev/",                          # overwrite a device
    r":\s*\(\s*\)\s*\{",                                # fork bomb :(){ :|:& };:
    r">\s*/dev/(sd|nvme|hd|mmcblk)",                    # clobber a disk
    r"\bchmod\s+-[a-z]*\s*777\s+/",                     # chmod -R 777 /
    r"\b(shutdown|reboot|halt|poweroff)\b",             # power control
    r"\binit\s+0\b",
    r">\s*/dev/sd",
    r"(curl|wget)\b[^\n]*\|\s*(sudo\s+)?(sh|bash|zsh)", # curl ... | sh
    r"\bsudo\s+rm\b",
]

_MAX_OUTPUT = 10_000


def run_command(command):
    """Execute a shell command with basic safeguards and return the output."""
    if not settings.allow_shell:
        return "Error: shell execution is disabled (set AIKU_ALLOW_SHELL=true to enable)."

    command = (command or "").strip()
    if not command:
        return "Error: empty command."

    logger.info(f"Terminal execution: {command}")
    if any(re.search(p, command, re.IGNORECASE) for p in _DANGEROUS_PATTERNS):
        logger.warning(f"Blocked dangerous command: {command}")
        return "Error: Command blocked for safety."

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=settings.shell_timeout,
        )
        output = (result.stdout or "") + (result.stderr or "")
        if not output:
            return "Command executed with no output."
        if len(output) > _MAX_OUTPUT:
            return output[:_MAX_OUTPUT] + f"\n\n[...truncated at {_MAX_OUTPUT} chars...]"
        return output
    except subprocess.TimeoutExpired:
        return "Error: Command timed out."
    except Exception as e:
        return f"Error: {str(e)}"
