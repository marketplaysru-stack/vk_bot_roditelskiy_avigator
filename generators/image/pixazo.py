"""generators/image/pixazo.py – генерация через Pixazo API"""
import os
import requests
import logging
from core.base import ImageGenerator

logger = logging.getLogger(__name__)

class PixazoGenerator(ImageGenerator):
    def __init__(self, api_key: str = None, timeout: int = 90):
        self.api_key = api_key or os.getenv("PIXAZO_API_KEY")
        self.timeout = timeout
        if not self.api_key:
            raise ValueError("PIXAZO_API_KEY не задан")
        self.base_url = os.getenv("PIXAZO_API_URL", "https://api.pixazo.com/v1/generate")

    def generate(self, prompt: str, negative_prompt: str = "", **kwargs) -> bytes:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt,
            "negative_prompt": negative_prompt or os.getenv("IMAGE_NEGATIVE_PROMPT", ""),
            "model": os.getenv("PIXAZO_DEFAULT_MODEL", "flux"),
            "width": int(os.getenv("IMAGE_WIDTH", 1024)),
            "height": int(os.getenv("IMAGE_HEIGHT", 1024)),
            "num_inference_steps": int(os.getenv("IMAGE_STEPS", 30)),
            "guidance_scale": float(os.getenv("IMAGE_CFG_SCALE", 7.0))
        }
        logger.info(f"Отправка запроса в Pixazo (таймаут {self.timeout} сек)")
        resp = requests.post(self.base_url, headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()
        result = resp.json()
        image_url = result.get("image_url")
        if not image_url:
            raise Exception("Pixazo не вернул URL")
        logger.info("Получен URL от Pixazo, скачиваем изображение")
        img_resp = requests.get(image_url, timeout=self.timeout)
        img_resp.raise_for_status()
        return img_resp.content