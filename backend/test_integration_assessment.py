import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ["MOCK_GEMINI"] = "true"

from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models import Employee, Competency

client = TestClient(app)

def test_assessment_generate():
    db = SessionLocal()
    employee = db.query(Employee).first()
    competency = db.query(Competency).first()
    db.close()

    if not employee or not competency:
        print("No employee or competency found in DB. Skipping.")
        return

    payload = {
        "employee_id": employee.id,
        "competency_id": competency.id,
        "number_of_questions": 3
    }
    response = client.post("/assessments/generate", json=payload)
    print("Status:", response.status_code)
    try:
        print("JSON:", response.json())
    except:
        print("Text:", response.text)

test_assessment_generate()
