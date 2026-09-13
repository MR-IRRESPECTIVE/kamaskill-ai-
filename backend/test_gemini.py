from unittest.mock import patch
from services.gemini_service import generate_text

@patch("services.gemini_service.client.models.generate_content")
def test_generate_text(mock_generate_content):
    class MockResponse:
        text = "mocked response"
    mock_generate_content.return_value = MockResponse()
    
    result = generate_text("Hello")
    assert result == "mocked response"
    mock_generate_content.assert_called_once()
