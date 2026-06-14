import secrets
import urllib.parse


def generate_image(prompt, width=1024, height=1024):
    """Return a deterministic-per-call image URL via Pollinations (no API key)."""
    if not prompt or not prompt.strip():
        return "Error: empty image prompt."
    seed = secrets.token_hex(4)
    query = urllib.parse.urlencode(
        {"seed": seed, "width": width, "height": height, "nologo": "true"}
    )
    return f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?{query}"
