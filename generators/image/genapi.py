"""generators/image/genapi.py – генерация через GenAPI (krea-v2) с правильной обработкой"""
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

        # Формируем payload с параметрами из документации
        payload = {
            "prompt": prompt,
            "model": kwargs.get("model", "medium"),
            "aspect_ratio": kwargs.get("aspect_ratio", "1:1"),
            "creativity": kwargs.get("creativity", "medium"),
            "image_style_references": kwargs.get("image_style_references", []),
            "styles": kwargs.get("styles", []),
            "moodboards": kwargs.get("moodboards", [
                {
                    "id": "1e51738c-7413-469e-93b6-ad50db460a1f",
                    "strength": 1
                }
            ])
        }
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        logger.info(f"Отправка запроса в GenAPI: {json.dumps(payload, ensure_ascii=False)[:300]}...")

        # 1) Отправляем запрос на генерацию
        resp = requests.post(self.base_url, headers=headers, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        result = resp.json()
        logger.info(f"Ответ GenAPI (создание задачи): {json.dumps(result, ensure_ascii=False)[:500]}")

        # 2) Проверяем, есть ли request_id
        request_id = result.get("request_id")
        if not request_id:
            # Если сразу вернулся готовый результат (output)
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
            raise Exception(f"GenAPI не вернул request_id и не дал готовый output: {result}")

        # 3) Если статус processing – ждём
        status = result.get("status")
        logger.info(f"Статус задачи: {status}, request_id: {request_id}")

        if status == "processing":
            logger.info(f"Ожидаем завершения генерации (request_id: {request_id})...")
            for attempt in range(30):  # до 60 секунд (по 2 сек)
                time.sleep(2)
                try:
                    status_resp = requests.get(
                        f"{self.status_url}/{request_id}",
                        headers=headers,
                        timeout=self.timeout
                    )
                    if status_resp.status_code == 404:
                        logger.warning(f"Задача {request_id} не найдена (404), возможно, она уже завершена или удалена")
                        # Может быть, статус уже success, но мы не можем проверить – выходим с ошибкой
                        raise Exception(f"Задача {request_id} не найдена (404)")
                    status_resp.raise_for_status()
                    status_data = status_resp.json()
                    logger.info(f"Попытка {attempt+1}: статус = {status_data.get('status')}")
                    if status_data.get("status") == "success":
                        result = status_data
                        break
                    elif status_data.get("status") == "error":
                        raise Exception(f"GenAPI ошибка: {status_data}")
                except requests.exceptions.RequestException as e:
                    logger.error(f"Ошибка при проверке статуса: {e}")
                    # Пробуем дальше
            else:
                raise Exception("Таймаут ожидания генерации")

        # 4) Проверяем финальный статус
        if result.get("status") != "success":
            raise Exception(f"GenAPI вернул ошибку: {result}")

        # 5) Извлекаем URL изображения
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