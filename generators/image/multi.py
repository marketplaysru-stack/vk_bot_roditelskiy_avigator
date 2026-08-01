"""generators/image/multi.py – Picsum + баннер (без GenAPI)"""
import logging
from typing import Optional
from .base import ImageGenerator
from .picsum import PicsumGenerator
from .banner import BannerGenerator

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.picsum = PicsumGenerator()
        self.banner = BannerGenerator()

    def generate(self, prompt: str, is_announce: bool = False, title: str = "", subtitle: str = "", cta: str = "") -> Optional[bytes]:
        category = self._detect_category(prompt)

        # Пытаемся получить случайное фото от Picsum
        bg_bytes = None
        try:
            bg_bytes = self.picsum.generate(prompt)
            if not bg_bytes:
                raise Exception("Picsum не вернул изображение")
        except Exception as e:
            logger.error(f"Picsum ошибка: {e}")

        # Если фото получено – накладываем текст
        if bg_bytes:
            try:
                if is_announce:
                    final = self.banner.create_banner_from_image(
                        bg_bytes,
                        title=title or "🔥 НОВОСТЬ",
                        subtitle=subtitle or prompt[:60],
                        cta=cta or "ПОДПИСЫВАЙСЯ"
                    )
                else:
                    final = self.banner.create_banner_from_image(
                        bg_bytes,
                        title=title or prompt[:50],
                        subtitle=subtitle or "Подробности в посте",
                        cta=cta or "ЧИТАТЬ"
                    )
                logger.info(f"Баннер создан, размер {len(final)} байт")
                return final
            except Exception as e:
                logger.error(f"Ошибка создания баннера: {e}")
                # Если не удалось наложить текст – возвращаем фон без текста
                return bg_bytes
        else:
            # Если фона нет – создаём баннер с нуля
            logger.warning("Нет фона, создаём баннер с нуля")
            if is_announce:
                return self.banner.create_banner(
                    title=title or "🔥 НОВОСТЬ",
                    subtitle=subtitle or prompt[:60],
                    cta=cta or "ПОДПИСЫВАЙСЯ",
                    category=category
                )
            else:
                return self.banner.create_banner(
                    title=title or prompt[:50],
                    subtitle=subtitle or "Подробности в посте",
                    cta=cta or "ЧИТАТЬ",
                    category=category
                )

    def _detect_category(self, prompt: str) -> str:
        topic = prompt.lower()
        if any(w in topic for w in ['строитель', 'архитектур', 'здание', 'ремонт', 'стройка', 'bim', 'кран', 'чертёж']):
            return "construction"
        elif any(w in topic for w in ['бизнес', 'предприним', 'стартап', 'инвест', 'финанс']):
            return "business"
        elif any(w in topic for w in ['ии', 'нейросет', 'ai', 'машинн', 'интеллект', 'чатгпт']):
            return "ai"
        else:
            return "general"

multi_image = MultiImageGenerator()