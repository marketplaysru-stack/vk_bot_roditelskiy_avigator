"""generators/image/pollinations.py"""
import requests
import urllib.parse
import os
import logging
from core.base import ImageGenerator

logger = logging.getLogger(__name__)

class PollinationsGenerator(ImageGenerator):
    def __init__(self, timeout=90):
        self.timeout = timeout
        self.base_url = os.getenv("POLLINATIONS_BASE_URL", "https://image.pollinations.ai")

    def generate(self, prompt, negative_prompt="", **kwargs):
        encoded = urllib.parse.quote(prompt)
        url = f"{self.base_url}/prompt/{encoded}?width=1024&height=1024&nologo=true&seed={hash(prompt) % 1000000}"
        logger.info(f"Запрос к Pollinations: {url[:100]}...")
        resp = requests.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp.content