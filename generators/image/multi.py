from core.base import ImageGenerator
import logging
import random
import os  # <-- добавлен импорт os

logger = logging.getLogger(__name__)

class PicsumGenerator(ImageGenerator):
    def __init__(self):
        self.width = int(os.getenv("IMAGE_WIDTH", "1024"))
        self.height = int(os.getenv("IMAGE_HEIGHT", "1024"))
        logger.info("PicsumGenerator инициализирован")

    def generate(self, prompt: str, **kwargs) -> str:
        seed = random.randint(1, 1000000)
        url = f"https://picsum.photos/seed/{seed}/{self.width}/{self.height}"
        logger.info(f"Picsum вернул URL: {url}")
        return url

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.generators = []
        try:
            self.generators.append(PicsumGenerator())
            logger.info("✅ PicsumGenerator добавлен (основной)")
        except Exception as e:
            logger.error(f"❌ Picsum не загружен: {e}")

        try:
            from generators.image.huggingface import HuggingFaceGenerator
            self.generators.append(HuggingFaceGenerator())
            logger.info("✅ HuggingFaceGenerator добавлен (резерв)")
        except Exception as e:
            logger.warning(f"❌ HuggingFace не загружен: {e}")

        try:
            from generators.image.agnes import AgnesImageGenerator
            self.generators.append(AgnesImageGenerator())
            logger.info("✅ AgnesImageGenerator добавлен (резерв)")
        except Exception as e:
            logger.warning(f"❌ Agnes не загружен: {e}")

        if not self.generators:
            from generators.image.dummy import DummyImageGenerator
            self.generators.append(DummyImageGenerator())
            logger.warning("✅ DummyImageGenerator добавлен (заглушка)")

    def generate(self, prompt: str, **kwargs) -> str:
        last_error = None
        for gen in self.generators:
            try:
                logger.info(f"🔄 Пробуем генератор {gen.__class__.__name__}")
                result = gen.generate(prompt, **kwargs)
                if result:
                    logger.info(f"✅ {gen.__class__.__name__} сгенерировал")
                    return result
            except Exception as e:
                logger.warning(f"❌ {gen.__class__.__name__} не сработал: {e}")
                last_error = e
        raise RuntimeError(f"Все генераторы не сработали. Последняя ошибка: {last_error}")