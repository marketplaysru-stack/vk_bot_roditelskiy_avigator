"""generators/image/multi.py"""
import logging
from typing import Optional
from .base import ImageGenerator
from .genapi import GenAPIGenerator          # Импортируем GenAPI
from .pollinations import PollinationsGenerator
from .picsum import PicsumGenerator
from .banner import BannerGenerator

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.generators = [
            ("GenAPI", GenAPIGenerator(timeout=120)),
            ("Pollinations", PollinationsGenerator(timeout=90)),
            ("Picsum", PicsumGenerator()),
        ]
        self.banner_generator = BannerGenerator()

    def generate(self, prompt: str, is_announce: bool = False, title: str = "", subtitle: str = "", cta: str = "") -> Optional[bytes]:
        category = self._detect_category(prompt)

        # Для анонсов – сразу баннер (или пробуем GenAPI, но оставим баннер для скорости)
        if is_announce:
            logger.info("Генерация баннера для анонса")
            try:
                return self.banner_generator.create_banner(
                    title=title or "🔥 НОВОСТЬ",
                    subtitle=subtitle or prompt[:60],
                    cta=cta or "ПОДПИСЫВАЙСЯ",
                    category=category
                )
            except Exception as e:
                logger.error(f"Ошибка баннера для анонса: {e}")
                # Если баннер не сработал, попробуем обычную генерацию
                pass

        # Для постов – пробуем генераторы по очереди
        detailed_prompt = self._build_detailed_prompt(prompt)
        for name, gen in self.generators:
            try:
                logger.info(f"Попытка генерации через {name}")
                result = gen.generate(detailed_prompt)
                if result and isinstance(result, bytes) and len(result) > 0:
                    logger.info(f"✅ Успешно через {name}, размер {len(result)} байт")
                    # Если это анонс (и мы не создали баннер) – накладываем текст
                    if is_announce:
                        return self.banner_generator.create_banner_from_image(
                            result,
                            title=title or "🔥 НОВОСТЬ",
                            subtitle=subtitle or prompt[:60],
                            cta=cta or "ПОДПИСЫВАЙСЯ"
                        )
                    return result
            except Exception as e:
                logger.error(f"{name} ошибка: {e}")

        # Если ничего не сработало – баннер-заглушка
        logger.warning("Все генераторы не сработали, создаём баннер-заглушку")
        if is_announce:
            return self.banner_generator.create_banner(
                title=title or "🔥 НОВОСТЬ",
                subtitle=subtitle or prompt[:60],
                cta=cta or "ПОДПИСЫВАЙСЯ",
                category=category
            )
        else:
            return self.banner_generator.create_banner(
                title=prompt[:50],
                subtitle="Подробности в посте",
                cta="ЧИТАТЬ",
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
        elif any(w in topic for w in ['образован', 'учёб', 'школ', 'университет', 'курс', 'лекция']):
            return "education"
        else:
            return "general"

    def _build_detailed_prompt(self, raw_prompt: str) -> str:
        topic = raw_prompt
        if "Анонс" in topic:
            if ":" in topic:
                parts = topic.split(":", 1)
                topic = parts[1].strip() if len(parts) > 1 else parts[0].strip()
            if "—" in topic:
                topic = topic.split("—")[0].strip()
        if len(topic) < 5:
            topic = "Технологии и инновации"

        return (
            f"Создай профессиональную иллюстрацию на тему: {topic}. "
            f"Включи элементы: графики, иконки, шестерёнки, схемы. "
            f"Стиль: современный плоский дизайн, яркие цвета: синий, фиолетовый, золотой. "
            f"Формат: вертикальный 9:16, высокое разрешение, без текста, без людей."
        )

multi_image = MultiImageGenerator()