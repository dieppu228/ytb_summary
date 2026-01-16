import os
from google import genai

class GeminiClient:
    def __init__(self, api_key: str | None = None, max_tokens: int = 100000):
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")

        self.client = genai.Client(api_key=api_key)
        self.models = self.client.models
        self.default_max_tokens = max_tokens

    def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int | None = None,
        temperature: float = 0.3,
        json_output: bool = False,
    ):
        if max_tokens is None:
            max_tokens = self.default_max_tokens
            
        config = {
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }

        if json_output:
            config["response_mime_type"] = "application/json"

        response = self.client.generate_text(
            model=model,
            prompt=prompt,
            **config
        )

        return response.text.strip()
