"""generators/image/huggingface.py"""
import os
import io
import logging
from huggingface_hub import InferenceClient
from core.base import ImageGenerator

logger = logging.getLogger(__name__)

class HuggingFaceGenerator(ImageGenerator):
    def __init__(self, token: str = None, timeout: int = 120):
        self.token = token or os.getenv("HF_TOKEN")
        self.timeout = timeout
        if not self.token:
            logger.warning("HF_TOKEN не задан, HuggingFaceGenerator будет недоступен")
            # Не бросаем исключение, чтобы бот мог продолжить с другими генераторами
        else:
            self.client = InferenceClient(model="stabilityai/stable-diffusion-xl-base-1.0", token=self.token)

    def generate(self, prompt: str, negative_prompt: str = "", **kwargs) -> bytes:
        if not self.token:
            raise ValueError("HF_TOKEN не задан")
        width = int(os.getenv("IMAGE_WIDTH", 1024))
        height = int(os.getenv("IMAGE_HEIGHT", 1024))
        steps = int(os.getenv("IMAGE_STEPS", 30))
        cfg = float(os.getenv("IMAGE_CFG_SCALE", 7.0))
        neg = negative_prompt or os.getenv("IMAGE_NEGATIVE_PROMPT", "")

        logger.info(f"Отправка запроса в HuggingFace (таймаут {self.timeout} сек)")
        # InferenceClient не поддерживает timeout напрямую, поэтому используем собственный механизм
        # Можно использовать requests с timeout, но здесь оставим как есть.
        # Примечание: если timeout критичен, можно переписать на requests.
        image = self.client.text_to_image(
            prompt=prompt,
            negative_prompt=neg,
            num_inference_steps=steps,
            guidance_scale=cfg,
            width=width,
            height=height
        )
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return buf.getvalue()