"""
services/providers/openrouter_provider.py

OpenRouter text-generation provider for Phase 1.
"""
import os
import json
import urllib.request
import urllib.error

from dotenv import load_dotenv

load_dotenv()

_API_KEY = os.getenv("OPENROUTER_API_KEY")
_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")

if not _API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set in the environment")


def generate_text(prompt: str) -> str:
    """Send prompt to OpenRouter and return the raw text response."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": _MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"OpenRouter HTTP Error {e.code}: {e.reason}\nBody: {error_body}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"OpenRouter Connection Error: {e.reason}")
        
    try:
        result = json.loads(response_body)
    except json.JSONDecodeError:
        raise ValueError("OpenRouter returned malformed JSON response")
        
    choices = result.get("choices")
    if not choices or len(choices) == 0:
        raise ValueError("OpenRouter response contains missing or empty choices")
        
    message = choices[0].get("message")
    if not message:
        raise ValueError("OpenRouter response choice is missing message")
        
    content = message.get("content")
    if not content:
        raise ValueError("OpenRouter response message has missing or empty content")
        
    return content
