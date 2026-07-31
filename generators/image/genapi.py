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
        self.poll_interval = 2  # секунды между проверками

    def generate(self, prompt: str, negative_prompt: str = "", **kwargs) -> bytes:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Отправляем задание
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
        logger.info(f"Первичный ответ: {result}")

        # Получаем request_id
        request_id = result.get("request_id")
        if not request_id:
            raise Exception(f"GenAPI не вернул request_id: {result}")

        # Статус может быть сразу "processing" или "success"
        status = result.get("status")
        if status == "success":
            output = result.get("output")
            if output:
                return self._get_image_from_output(output)
            else:
                raise Exception("Ответ success, но нет output")

        # Если статус processing – ждём
        if status == "processing":
            logger.info(f"Задача в обработке (request_id={request_id}), ожидаем...")
            # Используем GET-запрос для проверки статуса (если API поддерживает)
            # По примеру: возможно нужно использовать другой эндпоинт для получения статуса
            # Для простоты будем повторять POST с тем же payload? Но это неправильно.
            # Лучше использовать отдельный эндпоинт status, если он есть.
            # Пока заглушка: ждём фиксированное время и пробуем получить результат через тот же эндпоинт?
            # Реализуем простой polling через отдельный запрос (если API даёт возможность)
            # В документации GenAPI скорее всего есть /api/v1/requests/<request_id>
            status_url = f"https://api.gen-api.ru/api/v1/requests/{request_id}"
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                time.sleep(self.poll_interval)
                try:
                    status_resp = requests.get(status_url, headers=headers, timeout=30)
                    status_resp.raise_for_status()
                    status_data = status_resp.json()
                    logger.info(f"Статус задачи: {status_data}")
                    if status_data.get("status") == "success":
                        output = status_data.get("output")
                        if output:
                            return self._get_image_from_output(output)
                        else:
                            raise Exception("Статус success, но нет output")
                    elif status_data.get("status") == "failed":
                        raise Exception(f"Задача завершилась с ошибкой: {status_data}")
                except Exception as e:
                    logger.warning(f"Ошибка при проверке статуса: {e}")
                    continue
            raise Exception(f"Превышено время ожидания для request_id={request_id}")

        raise Exception(f"Неизвестный статус: {status}")

    def _get_image_from_output(self, output):
        """Извлекает URL изображения из поля output"""
        if isinstance(output, list) and len(output) > 0:
            image_url = output[0]
        elif isinstance(output, str):
            image_url = output
        else:
            raise Exception(f"Неожиданный формат output: {output}")
        if not image_url:
            raise Exception("URL изображения пуст")
        logger.info(f"Скачиваем изображение: {image_url}")
        img_resp = requests.get(image_url, timeout=self.timeout)
        img_resp.raise_for_status()
        return img_resp.content