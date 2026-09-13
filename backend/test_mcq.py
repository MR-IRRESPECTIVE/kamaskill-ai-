import pytest
from unittest.mock import patch
from services.mcq_engine import generate_mcqs

@patch("services.mcq_engine.generate_text")
def test_generate_mcqs(mock_generate_text):
    mock_generate_text.return_value = '{"questions": [{"question": "Test?", "options": {"A": "1", "B": "2", "C": "3", "D": "4"}, "correct_answer": "A", "explanation": "Exp", "difficulty": "Easy"}]}'
    result = generate_mcqs("Some text", 1)
    assert len(result["questions"]) == 1
    assert result["questions"][0]["question"] == "Test?"

@patch("services.mcq_engine.generate_text")
def test_generate_mcqs_invalid_json(mock_generate_text):
    mock_generate_text.return_value = "invalid json"
    with pytest.raises(ValueError, match="invalid JSON"):
        generate_mcqs("Some text", 1)
