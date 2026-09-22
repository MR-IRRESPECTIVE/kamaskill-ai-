import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ["MOCK_GEMINI"] = "true"

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_analyze_and_save():
    # Use existing test PDF
    pdf_path = "data_viz_guide.pdf"
    if not os.path.exists(pdf_path):
        pdf_path = "data_viz_fundamentals.pdf"

    with open(pdf_path, "rb") as f:
        response = client.post(
            "/materials/analyze-and-save?number_of_questions=3",
            files={"file": ("test.pdf", f, "application/pdf")}
        )
    print("Status:", response.status_code)
    try:
        print("JSON:", response.json())
    except:
        print("Text:", response.text)

test_analyze_and_save()
