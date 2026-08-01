"""generators/image/huggingface_inference.py – прямая HTTP-запрос к Hugging Face Inference API"""
import os
import io
import requests
import logging
from core.base import ImageGenerator

logger = logging.getLogger(__name__)

class HuggingFaceInferenceGenerator(ImageGenerator):
    def __init__(self, token: str = None, timeout: int = 120):
        self.token = token or os.getenv("HF_TOKEN")
        self.timeout = timeout
        if not self.token:
            raise ValueError("HF_TOKEN не задан")
        # Используем SDXL — чаще доступен бесплатно
        self.model = "stabilityai/stable-diffusion-xl-base-1.0"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"

    def generate(self, prompt: str, negative_prompt: str = "", **kwargs) -> bytes:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": negative_prompt or os.getenv("IMAGE_NEGATIVE_PROMPT", ""),
                "width": int(os.getenv("IMAGE_WIDTH", 1024)),
                "height": int(os.getenv("IMAGE_HEIGHT", 1024)),
                "num_inference_steps": int(os.getenv("IMAGE_STEPS", 30)),
                "guidance_scale": float(os.getenv("IMAGE_CFG_SCALE", 7.0))
            }
        }

        logger.info(f"Отправка запроса в Hugging Face (модель {self.model})")
        try:
            resp = requests.post(self.api_url, headers=headers, json=payload, timeout=self.timeout)
            logger.info(f"Статус ответа: {resp.status_code}")

            if resp.status_code == 200:
                # Ответ — бинарные данные (PNG)
                return resp.content
            else:
                # Пытаемся извлечь ошибку
                try:
                    error_data = resp.json()
                    error_msg = error_data.get("error", resp.text)
                except:
                    error_msg = resp.text
                raise Exception(f"HTTP {resp.status_code}: {error_msg}")
        except requests.exceptions.Timeout:
            logger.error("Таймаут при запросе к Hugging Face")
            raise
        except Exception as e:
            logger.error(f"Hugging Face ошибка: {e}")
            raise