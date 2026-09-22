import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ["MOCK_GEMINI"] = "true"

from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models import Employee, Competency, LearningMaterial, MaterialCompetency

client = TestClient(app)

def test_assessment_generate():
    db = SessionLocal()
    employee = db.query(Employee).first()
    competency = db.query(Competency).first()
    
    # Create a properly sectioned material
    material = LearningMaterial(
        title="Test Sectioned Material",
        filename="test.pdf",
        pages=1,
        extracted_text="1. First Section\nContent\n2. Second Section\nContent\n3. Third Section\nContent"
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    
    mc = MaterialCompetency(material_id=material.id, competency_id=competency.id, relevance=90)
    db.add(mc)
    db.commit()

    db.close()

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
