"""
services/providers/selector.py

Single point of provider selection.

Reads AI_PROVIDER from the environment. Supported values:
- gemini (default)
- openrouter
- mock

For backward compatibility, if AI_PROVIDER is not set, it checks MOCK_GEMINI.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def get_generate_text():
    """
    Return the appropriate generate_text() callable based on AI_PROVIDER or MOCK_GEMINI.
    """
    provider = os.getenv("AI_PROVIDER", "").strip().lower()
    
    if provider == "openrouter":
        from services.providers.openrouter_provider import generate_text
        return generate_text
        
    if provider == "mock":
        from services.providers.mock_provider import generate_text
        return generate_text
        
    if provider == "gemini":
        from services.providers.gemini_provider import generate_text
        return generate_text
        
    # Backward compatibility with MOCK_GEMINI if AI_PROVIDER is not set
    mock_flag = os.getenv("MOCK_GEMINI", "false").strip().lower()
    if mock_flag == "true":
        from services.providers.mock_provider import generate_text
        return generate_text

    # Default fallback: real Gemini provider
    from services.providers.gemini_provider import generate_text
    return generate_text
