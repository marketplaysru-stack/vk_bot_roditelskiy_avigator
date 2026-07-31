import requests, os
from core.base import ImageGenerator
class PicsumGenerator(ImageGenerator):
    def generate(self, prompt="", negative_prompt="", **kwargs):
        url = f"https://picsum.photos/1024/1024?random={hash(prompt)}"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.content