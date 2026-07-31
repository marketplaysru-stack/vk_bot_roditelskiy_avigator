"""generators/image/deepai.py – генерация изображений через DeepAI API"""
import os
import requests
import logging
from core.base import ImageGenerator

logger = logging.getLogger(__name__)

class DeepAIGenerator(ImageGenerator):
    def __init__(self, api_key: str = None, timeout: int = 90):
        self.api_key = api_key or os.getenv("DEEPAI_API_KEY")
        self.timeout = timeout
        if not self.api_key:
            raise ValueError("DEEPAI_API_KEY не задан")
        self.base_url = "https://api.deepai.org/api/text2img"

    def generate(self, prompt: str, negative_prompt: str = "", **kwargs) -> bytes:
        headers = {"api-key": self.api_key}
        data = {
            "text": prompt,
            "width": int(os.getenv("IMAGE_WIDTH", 1024)),
            "height": int(os.getenv("IMAGE_HEIGHT", 1024)),
            "grid_size": 1,
            "image_generator_version": "2"  # можно "1" или "2"
        }
        logger.info(f"Отправка запроса в DeepAI (таймаут {self.timeout} сек)")
        resp = requests.post(self.base_url, headers=headers, data=data, timeout=self.timeout)
        resp.raise_for_status()
        result = resp.json()
        
        # DeepAI возвращает ссылку в поле "output_url" или "id"
        image_url = result.get("output_url")
        if not image_url:
            # альтернативный формат ответа
            image_url = result.get("id")
            if image_url and not image_url.startswith("http"):
                image_url = f"https://api.deepai.org/job-view-file/{image_url}"
        if not image_url:
            raise Exception("DeepAI не вернул URL изображения")
        logger.info("Получен URL от DeepAI, скачиваем изображение")
        img_resp = requests.get(image_url, timeout=self.timeout)
        img_resp.raise_for_status()
        return img_resp.content