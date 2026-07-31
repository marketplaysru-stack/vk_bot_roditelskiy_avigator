"""generators/image/genapi.py – генерация через GenAPI (krea-v2)"""
import os
import requests
import logging
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
        data = {
            "callback_url": None,
            "prompt": prompt
        }
        # Можно добавить негативный промпт, если API поддерживает
        if negative_prompt:
            data["negative_prompt"] = negative_prompt

        logger.info(f"Отправка запроса в GenAPI (таймаут {self.timeout} сек)")
        resp = requests.post(self.base_url, headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()
        result = resp.json()

        # GenAPI возвращает ссылку на изображение в поле "image_url" или "url"
        image_url = result.get("image_url")
        if not image_url:
            # Возможно, в другом поле
            image_url = result.get("url")
        if not image_url:
            raise Exception("GenAPI не вернул URL изображения")
        logger.info("Получен URL от GenAPI, скачиваем изображение")
        img_resp = requests.get(image_url, timeout=self.timeout)
        img_resp.raise_for_status()
        return img_resp.content