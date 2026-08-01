"""generators/image/genapi.py – минимальный запрос к GenAPI"""
import os
import requests
import logging
import json
from core.base import ImageGenerator

logger = logging.getLogger(__name__)

class GenAPIGenerator(ImageGenerator):
    def __init__(self, api_key: str = None, timeout: int = 180):
        self.api_key = api_key or os.getenv("GENAPI_API_KEY")
        self.timeout = timeout
        if not self.api_key:
            raise ValueError("GENAPI_API_KEY не задан")
        self.url = "https://api.gen-api.ru/api/v1/networks/krea-v2"

    def generate(self, prompt: str, negative_prompt: str = "", **kwargs) -> bytes:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Минимальный payload – только prompt
        payload = {"prompt": prompt}
        # При необходимости можно добавить модель
        # payload["model"] = "krea-v2"
        # payload["aspect_ratio"] = "9:16"
        # payload["creativity"] = "medium"

        logger.info(f"Отправка запроса GenAPI: {json.dumps(payload, ensure_ascii=False)}")
        resp = requests.post(self.url, json=payload, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        result = resp.json()
        logger.info(f"Ответ GenAPI: {json.dumps(result, ensure_ascii=False)[:500]}")

        # Проверяем, есть ли output
        output = result.get("output")
        if output is None:
            # Если нет output, возможно, задача ещё обрабатывается
            raise Exception(f"GenAPI не вернул output: {result}")

        # Извлекаем URL
        if isinstance(output, list) and len(output) > 0:
            image_url = output[0]
        elif isinstance(output, str):
            image_url = output
        else:
            raise Exception(f"Неожиданный формат output: {output}")

        if not image_url:
            raise Exception("GenAPI не вернул URL изображения")

        logger.info(f"Скачиваем изображение: {image_url}")
        img_resp = requests.get(image_url, timeout=self.timeout)
        img_resp.raise_for_status()
        return img_resp.content