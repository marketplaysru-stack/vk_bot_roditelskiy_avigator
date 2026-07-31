"""generators/image/gemini.py – генерация изображений через Google Gemini API"""
import os
import requests
import logging
import base64
from core.base import ImageGenerator

logger = logging.getLogger(__name__)

class GeminiGenerator(ImageGenerator):
    def __init__(self, api_key: str = None, timeout: int = 120):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.timeout = timeout
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY не задан")
        # Модель для генерации изображений (preview)
        self.model = "gemini-2.5-flash-image-preview"
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def generate(self, prompt: str, negative_prompt: str = "", **kwargs) -> bytes:
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        # Gemini ожидает структурированный запрос
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 1.0,
                "topK": 32,
                "topP": 1.0,
                "maxOutputTokens": 2048,
            }
        }
        # Для изображений нужно указать responseModalities
        data["generationConfig"]["responseModalities"] = ["IMAGE"]
        # Дополнительно можно задать размер (но Gemini сам подбирает, можно указать в промпте)

        logger.info(f"Отправка запроса в Gemini (таймаут {self.timeout} сек)")
        resp = requests.post(self.base_url, headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()
        result = resp.json()

        # Извлекаем изображение из ответа
        try:
            # Gemini возвращает inlineData с base64-изображением
            inline_data = result["candidates"][0]["content"]["parts"][0]["inlineData"]
            image_bytes = base64.b64decode(inline_data["data"])
            logger.info(f"Изображение получено, размер {len(image_bytes)} байт")
            return image_bytes
        except (KeyError, IndexError) as e:
            logger.error(f"Не удалось извлечь изображение из ответа: {result}")
            raise Exception(f"Gemini не вернул изображение: {e}")