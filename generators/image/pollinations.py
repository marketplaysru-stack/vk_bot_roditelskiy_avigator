"""generators/image/pollinations.py"""
import os
import urllib.parse
import requests
import logging
from core.base import ImageGenerator

logger = logging.getLogger(__name__)

class PollinationsGenerator(ImageGenerator):
    def __init__(self, base_url: str = None, timeout: int = 60):
        self.base_url = base_url or os.getenv("POLLINATIONS_BASE_URL", "https://image.pollinations.ai")
        self.timeout = timeout

    def generate(self, prompt: str, negative_prompt: str = "", **kwargs) -> bytes:
        width = int(os.getenv("IMAGE_WIDTH", 1024))
        height = int(os.getenv("IMAGE_HEIGHT", 1024))
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"{self.base_url}/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
        logger.info(f"Запрос к Pollinations (таймаут {self.timeout} сек)")
        resp = requests.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp.content