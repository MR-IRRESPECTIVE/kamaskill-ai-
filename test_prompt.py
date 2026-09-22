import sys
sys.path.append('backend')
from services.mcq_engine import _build_batch_prompt
from services.providers.mock_provider import generate_text
import json

sections = [
    {"number": 1, "heading": "Intro", "body": "This is intro"},
    {"number": 2, "heading": "Body", "body": "This is body"}
]
prompt = _build_batch_prompt(sections)
print("PROMPT:")
print(prompt)

response = generate_text(prompt)
print("RESPONSE:")
print(response)

parsed = json.loads(response)
print("PARSED len:", len(parsed))
