import requests
import urllib.parse
from .base import ImageGenerator
from config import config

class PollinationsGenerator(ImageGenerator):
    def __init__(self):
        self.base_url = config.pollinations_url

    def generate(self, prompt: str) -> bytes:
        encoded = urllib.parse.quote(prompt)
        url = f"{self.base_url}/prompt/{encoded}?width=1024&height=1024&nologo=true"
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        return resp.content