"""generators/image/genapi.py – генерация через GenAPI (wan-2-7-image) с улучшенным получением результата"""
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
        self.base_url = "https://api.gen-api.ru/api/v1/networks/wan-2-7-image"
        self.status_url = "https://api.gen-api.ru/api/v1/requests"

    def generate(self, prompt: str, negative_prompt: str = "", **kwargs) -> bytes:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Формируем payload точно как в примере
        payload = {
            "callback_url": None,
            "prompt": prompt
        }
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        logger.info(f"Отправка запроса в GenAPI: {json.dumps(payload, ensure_ascii=False)[:200]}...")
        resp = requests.post(self.base_url, headers=headers, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        result = resp.json()
        logger.info(f"Ответ GenAPI (создание): {json.dumps(result, ensure_ascii=False)[:500]}")

        # Проверяем, есть ли output сразу
        output = result.get("output")
        if output:
            image_url = self._extract_url(output)
            if image_url:
                logger.info(f"Готовое изображение: {image_url}")
                return self._download_image(image_url)

        # Получаем request_id
        request_id = result.get("request_id")
        if not request_id:
            raise Exception(f"GenAPI не вернул request_id: {result}")

        logger.info(f"Задача создана, request_id: {request_id}")

        # Ожидаем завершения с увеличенной задержкой
        max_attempts = 40
        # Сначала ждём 5 секунд перед первой проверкой
        time.sleep(5)

        for attempt in range(max_attempts):
            # Пробуем получить статус
            try:
                status_resp = requests.get(
                    f"{self.status_url}/{request_id}",
                    headers=headers,
                    timeout=self.timeout
                )
                if status_resp.status_code == 404:
                    # Если /requests/{id} не найден, пробуем другой эндпоинт
                    logger.warning(f"Задача {request_id} не найдена по /requests, пробуем /requests/{request_id}/output")
                    output_resp = requests.get(
                        f"{self.status_url}/{request_id}/output",
                        headers=headers,
                        timeout=self.timeout
                    )
                    if output_resp.status_code == 200:
                        output_data = output_resp.json()
                        output_url = output_data.get("output") or output_data.get("url")
                        if output_url:
                            image_url = self._extract_url(output_url)
                            if image_url:
                                logger.info(f"Изображение получено через /output: {image_url}")
                                return self._download_image(image_url)
                    # Если и там ничего нет, продолжаем ждать
                elif status_resp.status_code == 200:
                    status_data = status_resp.json()
                    logger.info(f"Попытка {attempt+1}: статус = {status_data.get('status')}")
                    if status_data.get("status") == "success":
                        output = status_data.get("output")
                        if output:
                            image_url = self._extract_url(output)
                            if image_url:
                                logger.info(f"Изображение получено: {image_url}")
                                return self._download_image(image_url)
                        else:
                            logger.warning("Статус success, но output пуст")
                    elif status_data.get("status") == "error":
                        raise Exception(f"GenAPI ошибка: {status_data}")
                else:
                    logger.warning(f"Неизвестный статус ответа: {status_resp.status_code}")

            except Exception as e:
                logger.error(f"Ошибка проверки статуса: {e}")

            # Ждём 2 секунды перед следующей попыткой
            time.sleep(2)

        raise Exception("Таймаут ожидания генерации")

    def _extract_url(self, output):
        if isinstance(output, list) and len(output) > 0:
            return output[0]
        elif isinstance(output, str):
            return output
        elif isinstance(output, dict):
            return output.get("url") or output.get("image_url")
        return None

    def _download_image(self, url):
        img_resp = requests.get(url, timeout=self.timeout)
        img_resp.raise_for_status()
        return img_resp.content