import os
import requests
from .base import TextGenerator
from config import config

class AgnesGenerator(TextGenerator):
    def __init__(self):
        self.api_key = config.agnes_api_key
        self.timeout = 60
        self.base_url = "https://api.agnes.ai/v1/chat/completions"

    def generate(self, topic: str) -> str:
        if not self.api_key:
            raise ValueError("AGNES_API_KEY не задан")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "agnes-v1",
            "messages": [{"role": "user", "content": f"Напиши пост на тему: {topic}"}],
            "max_tokens": 300
        }
        resp = requests.post(self.base_url, headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]