"""generators/image/pexels.py – поиск бесплатных фото по ключевым словам"""
import os
import requests
import logging
from core.base import ImageGenerator

logger = logging.getLogger(__name__)

class PexelsGenerator(ImageGenerator):
    def __init__(self, api_key: str = None, timeout: int = 30):
        self.api_key = api_key or os.getenv("PEXELS_API_KEY")
        self.timeout = timeout
        self.base_url = "https://api.pexels.com/v1/search"

    def generate(self, prompt: str, negative_prompt: str = "", **kwargs) -> bytes:
        keywords = self._extract_keywords(prompt)
        if not keywords:
            keywords = "technology"

        headers = {"Authorization": self.api_key} if self.api_key else {}
        params = {"query": keywords, "per_page": 5, "page": 1}

        try:
            resp = requests.get(self.base_url, headers=headers, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            photos = data.get("photos", [])
            if not photos:
                raise Exception("Нет фото по запросу")
            # Берём первое фото (можно рандомизировать)
            photo_url = photos[0]["src"]["large2x"]
            logger.info(f"Скачиваем фото с Pexels: {photo_url}")
            img_resp = requests.get(photo_url, timeout=self.timeout)
            img_resp.raise_for_status()
            return img_resp.content
        except Exception as e:
            logger.error(f"Pexels ошибка: {e}")
            raise

    def _extract_keywords(self, prompt: str) -> str:
        stopwords = {'иллюстрация', 'на', 'тему', 'про', 'о', 'и', 'в', 'с', 'без', 'для', 'стиль', 'цвет', 'формат'}
        words = prompt.lower().split()
        keywords = [w for w in words if w not in stopwords and len(w) > 3]
        return ' '.join(keywords[:4]) if keywords else "technology"