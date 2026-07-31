import random
import logging
from typing import Optional
from .base import ImageGenerator
from .picsum import PicsumGenerator
from .pollinations import PollinationsGenerator
from config import config

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.generators = [
            PollinationsGenerator(),
            PicsumGenerator(),
        ]

    def generate(self, prompt: str) -> Optional[bytes]:
        # Попробуем улучшить промпт с помощью текстового генератора (если есть)
        for gen in self.generators:
            try:
                result = gen.generate(prompt)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Генератор {gen.__class__.__name__} не сработал: {e}")
        return None

multi_image = MultiImageGenerator()