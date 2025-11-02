import os
import requests
import json
import time
from app.config import settings

class GeminiAIService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key or self.api_key == "YOUR_GEMINI_API_KEY":
            raise ValueError("GEMINI_API_KEY is not set in environment variables or is default.")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"

    def call_gemini_api(self, prompt: str, response_type: str = 'text'):
        if not self.api_key or self.api_key == 'YOUR_GEMINI_API_KEY':
            raise ValueError("Gemini API 키가 설정되지 않았습니다.")

        url = f"{self.base_url}?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.6, "topK": 1, "topP": 1, "maxOutputTokens": 8192}
        }
        headers = {
            'Content-Type': 'application/json'
        }

        max_retries = 3
        for i in range(max_retries):
            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
                response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
                break
            except requests.exceptions.RequestException as e:
                if i < max_retries - 1:
                    print(f"API 호출 실패 (시도 {i + 1}/{max_retries}), 오류: {e}. 5초 후 재시도합니다.")
                    time.sleep(5)
                else:
                    raise ConnectionError(f"Gemini API 호출 실패: {e}")

        json_response = response.json()

        if not json_response.get('candidates') or not json_response['candidates'][0].get('content') or not json_response['candidates'][0]['content'].get('parts'):
            raise ValueError(f"Gemini API 응답 형식이 올바르지 않습니다: {json_response}")

        result_text = json_response['candidates'][0]['content']['parts'][0]['text']
        if response_type == 'html':
            result_text = result_text.replace('```html\n', '').replace('\n```', '')
        return result_text
