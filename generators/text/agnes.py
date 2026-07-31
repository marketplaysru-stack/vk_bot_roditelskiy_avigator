"""
generators/text/agnes.py
---------------------------------------
Генерация текста через Agnes API.
"""

from __future__ import annotations

from config import settings
from core.http import http

from models.post import Post

from generators.text.base import BaseTextGenerator


class AgnesGenerator(BaseTextGenerator):

    name = "agnes"

    API_URL = "https://api.agnes.ai/v1/chat/completions"

    def generate(
        self,
        topic: str,
        **kwargs,
    ) -> Post:

        self.before_generate(topic)

        prompt = kwargs.get(
            "prompt",
            f"Напиши интересный пост на тему:\n\n{topic}"
        )

        payload = {
            "model": "agnes-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": 0.8,
        }

        headers = {
            "Authorization": f"Bearer {settings.AGNES_API_KEY}",
            "Content-Type": "application/json",
        }

        data = http.post_json(
            self.API_URL,
            json=payload,
            headers=headers,
        )

        text = (
            data["choices"][0]["message"]["content"]
            .strip()
        )

        post = Post(
            title=topic,
            text=text,
        )

        return self.after_generate(post)