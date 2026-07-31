"""generators/image/genapi.py – генерация через GenAPI (krea-v2)"""
import os
import requests
import logging
import json
from core.base import ImageGenerator

logger = logging.getLogger(__name__)

class GenAPIGenerator(ImageGenerator):
    def __init__(self, api_key: str = None, timeout: int = 120):
        self.api_key = api_key or os.getenv("GENAPI_API_KEY")
        self.timeout = timeout
        if not self.api_key:
            raise ValueError("GENAPI_API_KEY не задан")
        self.base_url = "https://api.gen-api.ru/api/v1/networks/krea-v2"

    def generate(self, prompt: str, negative_prompt: str = "", **kwargs) -> bytes:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Формируем запрос по документации GenAPI
        payload = {
            "callback_url": None,
            "prompt": prompt
        }

        # Добавляем негативный промпт, если есть
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        # Можно добавить параметры модели (если API поддерживает)
        # payload["model"] = "krea-v2"
        # payload["width"] = 1024
        # payload["height"] = 1024

        logger.info(f"Отправка запроса в GenAPI: {json.dumps(payload, ensure_ascii=False)[:200]}...")
        resp = requests.post(self.base_url, headers=headers, json=payload, timeout=self.timeout)

        # Логируем ответ для отладки
        logger.info(f"Статус ответа: {resp.status_code}")
        try:
            result = resp.json()
            logger.info(f"Ответ GenAPI: {json.dumps(result, ensure_ascii=False)[:500]}")
        except:
            logger.error(f"Не JSON ответ: {resp.text[:200]}")
            resp.raise_for_status()

        # Проверяем статус
        if resp.status_code != 200:
            raise Exception(f"GenAPI ошибка {resp.status_code}: {result}")

        # Извлекаем URL изображения
        output = result.get("output")
        if output is None:
            raise Exception(f"GenAPI не вернул поле output: {result}")

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