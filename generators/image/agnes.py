from core.base import ImageGenerator
import logging
logger = logging.getLogger(__name__)

class AgnesImageGenerator(ImageGenerator):
    def __init__(self):
        self.api_key = None
        logger.warning("AgnesImageGenerator не настроен (нет ключа)")

    def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError("AgnesImageGenerator не реализован")