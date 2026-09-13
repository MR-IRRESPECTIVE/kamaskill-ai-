import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set in the .env file"
    )

client = genai.Client(api_key=API_KEY)


def generate_text(prompt: str):

    interaction = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return interaction.text
