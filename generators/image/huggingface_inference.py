"""generators/image/huggingface_inference.py – генерация через Hugging Face Inference API"""
import os
import io
import requests
import logging
from huggingface_hub import InferenceClient
from core.base import ImageGenerator

logger = logging.getLogger(__name__)

class HuggingFaceInferenceGenerator(ImageGenerator):
    def __init__(self, token: str = None, timeout: int = 120):
        self.token = token or os.getenv("HF_TOKEN")
        self.timeout = timeout
        if not self.token:
            raise ValueError("HF_TOKEN не задан")
        # Используем модель FLUX.1-dev (качественная) или SDXL
        self.model = "black-forest-labs/FLUX.1-dev"  # можно заменить на "stabilityai/stable-diffusion-xl-base-1.0"
        self.client = InferenceClient(model=self.model, token=self.token)

    def generate(self, prompt: str, negative_prompt: str = "", **kwargs) -> bytes:
        try:
            logger.info(f"Отправка запроса в Hugging Face (модель {self.model})")
            # InferenceClient возвращает PIL Image или список изображений
            image = self.client.text_to_image(
                prompt=prompt,
                negative_prompt=negative_prompt or os.getenv("IMAGE_NEGATIVE_PROMPT", ""),
                num_inference_steps=int(os.getenv("IMAGE_STEPS", 30)),
                guidance_scale=float(os.getenv("IMAGE_CFG_SCALE", 7.0)),
                width=int(os.getenv("IMAGE_WIDTH", 1024)),
                height=int(os.getenv("IMAGE_HEIGHT", 1024))
            )
            # Сохраняем в байты
            buf = io.BytesIO()
            image.save(buf, format='PNG')
            return buf.getvalue()
        except Exception as e:
            logger.error(f"Hugging Face ошибка: {e}")
            raise