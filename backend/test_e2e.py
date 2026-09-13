from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock
import json

client = TestClient(app)

class MockInteraction:
    text = json.dumps({
        "questions": [
            {
                "question": "Q1",
                "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
                "correct_answer": "A",
                "explanation": "Exp",
                "difficulty": "Easy"
            }
        ],
        "competencies": [
            {"name": "Data Analysis", "relevance": 90}
        ]
    })

@patch("routers.materials.PdfReader")
@patch("services.gemini_service.client.models.generate_content")
def test_end_to_end_flow(mock_generate_content, mock_pdf_reader):
    mock_generate_content.return_value = MockInteraction()
    
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Mocked PDF content"
    mock_reader_instance = MagicMock()
    mock_reader_instance.pages = [mock_page]
    mock_pdf_reader.return_value = mock_reader_instance

    resp = client.get("/employees/1")
    assert resp.status_code == 200

    resp = client.get("/competencies/employee/1")
    assert resp.status_code == 200

    resp = client.get("/recommendations/employee/1")
    assert resp.status_code == 200

    files = {"file": ("test.pdf", b"mocked", "application/pdf")}
    data = {"number_of_questions": 1}
    resp = client.post("/materials/analyze-and-save", files=files, data=data)
    assert resp.status_code == 200, resp.text
    quiz_id = resp.json()["quiz"]["id"]

    resp = client.get(f"/quizzes/{quiz_id}")
    assert resp.status_code == 200
    assert "correct_answer" not in resp.json()["questions"][0]

    payload = {
        "employee_id": 1,
        "answers": [{"question_id": resp.json()["questions"][0]["id"], "answer": "A"}]
    }
    resp = client.post(f"/quizzes/{quiz_id}/attempt", json=payload)
    assert resp.status_code == 200
    result_json = resp.json()
    assert result_json["result"]["percentage"] == 100.0
    assert "new_competency_level" in result_json
