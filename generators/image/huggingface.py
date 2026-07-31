"""generators/image/huggingface.py"""
import os
import io
import requests
import logging
from core.base import ImageGenerator

logger = logging.getLogger(__name__)

class HuggingFaceGenerator(ImageGenerator):
    def __init__(self, token: str = None, timeout: int = 120):
        self.token = token or os.getenv("HF_TOKEN")
        self.timeout = timeout
        if not self.token:
            raise ValueError("HF_TOKEN не задан")
        # Используем Inference API (бесплатный)
        self.api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

    def generate(self, prompt: str, negative_prompt: str = "", **kwargs) -> bytes:
        headers = {"Authorization": f"Bearer {self.token}"}
        # Для SDXL можно передавать параметры в payload
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": negative_prompt or os.getenv("IMAGE_NEGATIVE_PROMPT", ""),
                "width": int(os.getenv("IMAGE_WIDTH", 1024)),
                "height": int(os.getenv("IMAGE_HEIGHT", 1024)),
                "num_inference_steps": int(os.getenv("IMAGE_STEPS", 30)),
                "guidance_scale": float(os.getenv("IMAGE_CFG_SCALE", 7.0)),
            }
        }
        logger.info(f"Отправка запроса в Hugging Face (таймаут {self.timeout} сек)")
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=self.timeout)
        if response.status_code == 200:
            return response.content  # изображение в байтах
        else:
            error_msg = f"Ошибка Hugging Face: {response.status_code} {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)