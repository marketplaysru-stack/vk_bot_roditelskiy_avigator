from core.base import ImageGenerator
import logging
logger = logging.getLogger(__name__)

class HuggingFaceGenerator(ImageGenerator):
    def __init__(self):
        self.token = None
        logger.warning("HuggingFaceGenerator не настроен (нет ключа)")

    def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError("HuggingFaceGenerator не реализован")