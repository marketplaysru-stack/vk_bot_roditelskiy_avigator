"""generators/image/genapi.py – генерация через GenAPI (krea-v2) с ожиданием"""
import os
import requests
import logging
import json
import time
from core.base import ImageGenerator

logger = logging.getLogger(__name__)

class GenAPIGenerator(ImageGenerator):
    def __init__(self, api_key: str = None, timeout: int = 120):
        self.api_key = api_key or os.getenv("GENAPI_API_KEY")
        self.timeout = timeout
        if not self.api_key:
            raise ValueError("GENAPI_API_KEY не задан")
        self.base_url = "https://api.gen-api.ru/api/v1/networks/krea-v2"
        self.status_url = "https://api.gen-api.ru/api/v1/requests"

    def generate(self, prompt: str, negative_prompt: str = "", **kwargs) -> bytes:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 1) Отправляем запрос на генерацию
        payload = {
            "prompt": prompt,
            "callback_url": None
        }
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        logger.info(f"Отправка запроса в GenAPI: {json.dumps(payload, ensure_ascii=False)[:200]}...")
        resp = requests.post(self.base_url, headers=headers, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        result = resp.json()
        logger.info(f"Ответ GenAPI: {json.dumps(result, ensure_ascii=False)[:500]}")

        # 2) Если статус processing – ждём завершения
        if result.get("status") == "processing":
            request_id = result.get("request_id")
            if not request_id:
                raise Exception("GenAPI не вернул request_id")
            logger.info(f"Генерация в процессе, request_id: {request_id}, ожидаем...")
            # Ждём до 60 секунд, проверяя статус
            for _ in range(30):  # 30 попыток по 2 секунды = 60 сек
                time.sleep(2)
                status_resp = requests.get(
                    f"{self.status_url}/{request_id}",
                    headers=headers,
                    timeout=self.timeout
                )
                status_resp.raise_for_status()
                status_data = status_resp.json()
                logger.info(f"Статус: {status_data.get('status')}")
                if status_data.get("status") == "success":
                    result = status_data
                    break
                elif status_data.get("status") == "error":
                    raise Exception(f"GenAPI ошибка: {status_data}")
            else:
                raise Exception("Таймаут ожидания генерации")

        # 3) Проверяем, что статус success
        if result.get("status") != "success":
            raise Exception(f"GenAPI вернул ошибку: {result}")

        # 4) Извлекаем URL
        output = result.get("output")
        if output is None:
            raise Exception(f"GenAPI не вернул output: {result}")

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