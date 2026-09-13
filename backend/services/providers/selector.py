"""
services/providers/selector.py

Single point of provider selection.

Reads MOCK_GEMINI from the environment (loaded from .env by dotenv).
Default is false (real Gemini).  The mock provider is only active when
MOCK_GEMINI=true is explicitly set.

Usage inside mcq_engine.py:
    from services.providers.selector import get_generate_text
    generate_text = get_generate_text()
"""
import os
from dotenv import load_dotenv

load_dotenv()


def get_generate_text():
    """
    Return the appropriate generate_text() callable based on MOCK_GEMINI.

    Returns gemini_provider.generate_text unless MOCK_GEMINI is explicitly
    set to the string 'true' (case-insensitive).
    """
    mock_flag = os.getenv("MOCK_GEMINI", "false").strip().lower()

    if mock_flag == "true":
        from services.providers.mock_provider import generate_text
        return generate_text

    # Default: real Gemini provider
    from services.providers.gemini_provider import generate_text
    return generate_text
