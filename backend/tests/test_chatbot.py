from fastapi.testclient import TestClient
from unittest.mock import patch

def test_chat_with_bot(client: TestClient):
    with patch('backend.app.services.chatbot_service.GeminiAIService.call_gemini_api') as mock_gemini:
        # Mock the routing and final response
        mock_gemini.side_effect = [
            '[]',  # Empty tool calls
            'Hello from the mock bot!' # Final response
        ]

        response = client.post("/api/v1/chat", json={"message": "Hello"})
        
        assert response.status_code == 200
        assert response.json() == {"type": "text", "content": "Hello from the mock bot!"}
