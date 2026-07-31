import requests
from .base import ImageGenerator

class PicsumGenerator(ImageGenerator):
    def generate(self, prompt: str = "") -> bytes:
        width = 1024
        height = 1024
        url = f"https://picsum.photos/{width}/{height}?random={hash(prompt) & 0x7fffffff}"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.content