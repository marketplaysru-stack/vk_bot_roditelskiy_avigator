"""generators/image/picsum.py – случайное фото"""
import requests
import os
from core.base import ImageGenerator

class PicsumGenerator(ImageGenerator):
    def generate(self, prompt: str = "", negative_prompt: str = "", **kwargs) -> bytes:
        width = int(os.getenv("IMAGE_WIDTH", 1024))
        height = int(os.getenv("IMAGE_HEIGHT", 1024))
        url = f"https://picsum.photos/{width}/{height}?random={hash(prompt) & 0x7fffffff}"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.content