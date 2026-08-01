"""generators/image/genapi.py – генерация через GenAPI"""
import os
import requests
import logging
import json
import time
from core.base import ImageGenerator

logger = logging.getLogger(__name__)

class GenAPIGenerator(ImageGenerator):
    def __init__(self, api_key: str = None, timeout: int = 180):
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
        payload = {
            "callback_url": None,
            "prompt": prompt,
        }
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        logger.info(f"Отправка запроса в GenAPI: {json.dumps(payload, ensure_ascii=False)[:200]}...")
        resp = requests.post(self.base_url, headers=headers, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        result = resp.json()
        logger.info(f"Ответ GenAPI (создание): {json.dumps(result, ensure_ascii=False)[:500]}")

        # Если сразу есть output
        output = result.get("output")
        if output:
            if isinstance(output, list) and len(output) > 0:
                image_url = output[0]
            elif isinstance(output, str):
                image_url = output
            else:
                image_url = output
            if image_url:
                logger.info(f"Готовое изображение: {image_url}")
                img_resp = requests.get(image_url, timeout=self.timeout)
                img_resp.raise_for_status()
                return img_resp.content

        request_id = result.get("request_id")
        if not request_id:
            raise Exception(f"GenAPI не вернул request_id: {result}")

        logger.info(f"Задача создана, request_id: {request_id}")
        for attempt in range(30):
            time.sleep(2)
            try:
                status_resp = requests.get(
                    f"{self.status_url}/{request_id}",
                    headers=headers,
                    timeout=self.timeout
                )
                if status_resp.status_code == 404:
                    # Пробуем /output
                    output_resp = requests.get(
                        f"{self.status_url}/{request_id}/output",
                        headers=headers,
                        timeout=self.timeout
                    )
                    if output_resp.status_code == 200:
                        output_data = output_resp.json()
                        image_url = output_data.get("output") or output_data.get("url")
                        if image_url:
                            logger.info(f"Изображение получено через /output: {image_url}")
                            img_resp = requests.get(image_url, timeout=self.timeout)
                            img_resp.raise_for_status()
                            return img_resp.content
                    continue
                status_resp.raise_for_status()
                status_data = status_resp.json()
                logger.info(f"Попытка {attempt+1}: статус = {status_data.get('status')}")
                if status_data.get("status") == "success":
                    output = status_data.get("output")
                    if output:
                        if isinstance(output, list) and len(output) > 0:
                            image_url = output[0]
                        elif isinstance(output, str):
                            image_url = output
                        else:
                            image_url = output
                        if image_url:
                            logger.info(f"Изображение получено: {image_url}")
                            img_resp = requests.get(image_url, timeout=self.timeout)
                            img_resp.raise_for_status()
                            return img_resp.content
                    break
                elif status_data.get("status") == "error":
                    raise Exception(f"GenAPI ошибка: {status_data}")
            except Exception as e:
                logger.error(f"Ошибка проверки статуса: {e}")
        else:
            raise Exception("Таймаут ожидания генерации")
        raise Exception("Не удалось получить изображение")