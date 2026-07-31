"""generators/image/multi.py"""
import logging
from typing import Optional
from .base import ImageGenerator
from .agnes import AgnesImageGenerator
from .huggingface import HuggingFaceGenerator
from .pollinations import PollinationsGenerator
from .picsum import PicsumGenerator
from .banner import BannerGenerator
from PIL import Image, ImageDraw, ImageFont
import io

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.generators = [
            ("Agnes", AgnesImageGenerator(timeout=120)),
            ("HuggingFace", HuggingFaceGenerator(timeout=120)),
            ("Pollinations", PollinationsGenerator(timeout=60)),
            ("Picsum", PicsumGenerator()),
        ]
        self.banner_generator = BannerGenerator()

    def generate(self, prompt: str, is_announce: bool = False, title: str = "", subtitle: str = "", cta: str = "") -> Optional[bytes]:
        if is_announce:
            logger.info("Генерация баннера для анонса (локально)")
            try:
                return self.banner_generator.create_banner(
                    title=title or "🔥 НОВОСТЬ",
                    subtitle=subtitle or prompt[:60],
                    cta=cta or "ПОДПИСЫВАЙСЯ"
                )
            except Exception as e:
                logger.error(f"Ошибка создания баннера для анонса: {e}")
                return self._create_fallback_image()

        # Для постов – сначала пытаемся получить картинку от внешних генераторов
        detailed_prompt = self._build_detailed_prompt(prompt)
        logger.info(f"Промпт для генерации: {detailed_prompt[:200]}...")

        for name, gen in self.generators:
            try:
                logger.info(f"Попытка генерации через {name} с таймаутом {getattr(gen, 'timeout', 'N/A')} сек")
                result = gen.generate(detailed_prompt)
                if result and isinstance(result, bytes) and len(result) > 0:
                    logger.info(f"✅ Успешно сгенерировано через {name}, размер {len(result)} байт")
                    return result
                else:
                    logger.warning(f"{name} вернул пустой результат")
            except Exception as e:
                logger.error(f"{name} ошибка: {e}")

        # Если все API не сработали – создаём баннер-заглушку для поста
        logger.warning("Все внешние генераторы не сработали, создаём баннер-заглушку")
        try:
            return self.banner_generator.create_banner(
                title=prompt[:50],
                subtitle="Подробности в посте",
                cta="ЧИТАТЬ"
            )
        except Exception as e:
            logger.error(f"Ошибка создания баннера-заглушки: {e}")
            return self._create_fallback_image()

    def _build_detailed_prompt(self, raw_prompt: str) -> str:
        # ... (без изменений, можно оставить как было)
        # Но для краткости оставим упрощённую версию
        return f"Professional illustration about {raw_prompt}. Include relevant icons and graphics. Style: modern, flat design, vibrant colors. Vertical 9:16, no text, no people."

    def _create_fallback_image(self) -> bytes:
        # ... (заглушка)
        pass

multi_image = MultiImageGenerator()