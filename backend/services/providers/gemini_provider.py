"""
services/providers/gemini_provider.py

Real Gemini text-generation provider.
This is the default provider used in production.
It is unchanged from the original gemini_service.py integration.
"""
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

_API_KEY = os.getenv("GEMINI_API_KEY")

if not _API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the .env file")

_client = genai.Client(api_key=_API_KEY)


def generate_text(prompt: str) -> str:
    """Send prompt to Gemini and return the raw text response."""
    interaction = _client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return interaction.text
