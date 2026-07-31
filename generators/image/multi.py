"""generators/image/multi.py"""
import logging
from typing import Optional
from .base import ImageGenerator
from .pollinations import PollinationsGenerator
from .picsum import PicsumGenerator
from .banner import BannerGenerator
from PIL import Image, ImageDraw, ImageFont
import io

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        # Только рабочие генераторы
        self.generators = [
            ("Pollinations", PollinationsGenerator(timeout=90)),
            ("Picsum", PicsumGenerator()),
        ]
        self.banner_generator = BannerGenerator()

    def generate(self, prompt: str, is_announce: bool = False, title: str = "", subtitle: str = "", cta: str = "") -> Optional[bytes]:
        detailed_prompt = self._build_detailed_prompt(prompt)
        logger.info(f"Промпт для генерации: {detailed_prompt[:200]}...")

        image_bytes = None
        for name, gen in self.generators:
            try:
                logger.info(f"Попытка генерации через {name}")
                result = gen.generate(detailed_prompt)
                if result and isinstance(result, bytes) and len(result) > 0:
                    logger.info(f"✅ Успешно через {name}, размер {len(result)} байт")
                    image_bytes = result
                    break
            except Exception as e:
                logger.error(f"{name} ошибка: {e}")

        if not image_bytes:
            logger.warning("Генераторы не дали результат, создаём баннер")
            try:
                if is_announce:
                    return self.banner_generator.create_banner(
                        title=title or "🔥 НОВОСТЬ",
                        subtitle=subtitle or prompt[:60],
                        cta=cta or "ПОДПИСЫВАЙСЯ",
                        category=self._detect_category(prompt)
                    )
                else:
                    return self.banner_generator.create_banner(
                        title=prompt[:50],
                        subtitle="Подробности в посте",
                        cta="ЧИТАТЬ",
                        category=self._detect_category(prompt)
                    )
            except Exception as e:
                logger.error(f"Ошибка баннера: {e}")
                return self._create_fallback_image()

        if is_announce:
            try:
                return self.banner_generator.create_banner_from_image(
                    image_bytes,
                    title=title or "🔥 НОВОСТЬ",
                    subtitle=subtitle or prompt[:60],
                    cta=cta or "ПОДПИСЫВАЙСЯ"
                )
            except Exception as e:
                logger.error(f"Ошибка наложения текста: {e}")
                return image_bytes

        return image_bytes

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
            topic = "технологии и инновации"

        category = self._detect_category(topic)

        # Промпт на русском (Pollinations понимает русский, но лучше добавить английский)
        templates_ru = {
            "construction": f"Иллюстрация на тему: {topic}. Стройка, краны, чертежи, каски, здания, BIM. Стиль: плоский дизайн, яркие цвета: синий, оранжевый, белый. Вертикальный формат 9:16, без текста, без людей.",
            "business": f"Иллюстрация на тему: {topic}. Графики роста, диаграммы, шестерёнки, рукопожатия, доллары. Стиль: современный, деловой. Цвета: тёмно-синий, золотой, белый. Вертикальный формат, без текста, без людей.",
            "ai": f"Иллюстрация на тему: {topic}. Нейросети, ИИ-чипы, потоки данных, светящиеся схемы. Стиль: киберпанк, неон. Цвета: фиолетовый, синий, голубой, золотой. Вертикальный формат, без текста, без людей.",
            "education": f"Иллюстрация на тему: {topic}. Книги, диплом, лампочка, глобус, карандаши. Стиль: красочный, плоский. Цвета: синий, жёлтый, зелёный, белый. Вертикальный формат, без текста, без людей.",
            "general": f"Иллюстрация на тему: {topic}. Абстрактные иконки, геометрические фигуры. Стиль: современный, чистый, плоский. Цвета: синий, фиолетовый, оранжевый, белый. Вертикальный формат, без текста, без людей."
        }
        return templates_ru.get(category, templates_ru["general"])

    def _create_fallback_image(self) -> bytes:
        try:
            width, height = 800, 600
            img = Image.new('RGB', (width, height), color='#0a0a2e')
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            except:
                font = ImageFont.load_default()
            text = "AI Навигатор"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            draw.text((x, y), text, fill='#FFD700', font=font)
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            return buf.getvalue()
        except:
            return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9c\x63\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc\xccY\xe7\x00\x00\x00\x00IEND\xaeB`\x82'

multi_image = MultiImageGenerator()