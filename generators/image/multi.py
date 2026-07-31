"""generators/image/multi.py"""
import random
import logging
from typing import Optional
from .base import ImageGenerator
from .picsum import PicsumGenerator
from .pollinations import PollinationsGenerator

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.generators = [
            PollinationsGenerator(),
            PicsumGenerator(),
        ]

    def generate(self, prompt: str) -> Optional[bytes]:
        for gen in self.generators:
            try:
                logger.info(f"Попытка генерации через {gen.__class__.__name__}")
                result = gen.generate(prompt)
                if result and isinstance(result, bytes) and len(result) > 0:
                    logger.info(f"Успешно, размер {len(result)} байт")
                    return result
                else:
                    logger.warning(f"Генератор вернул пустой результат")
            except Exception as e:
                logger.warning(f"{gen.__class__.__name__} не сработал: {e}")
        return None

multi_image = MultiImageGenerator()