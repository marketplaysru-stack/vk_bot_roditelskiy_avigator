"""generators/image/multi.py"""
import logging
from typing import Optional
from .base import ImageGenerator
from .huggingface import HuggingFaceGenerator
from .pollinations import PollinationsGenerator
from .picsum import PicsumGenerator
from .banner import BannerGenerator

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.generators = [
            ("HuggingFace", HuggingFaceGenerator(timeout=120)),
            ("Pollinations", PollinationsGenerator(timeout=90)),
            ("Picsum", PicsumGenerator()),
        ]
        self.banner_generator = BannerGenerator()

    def generate(self, prompt: str, is_announce: bool = False, title: str = "", subtitle: str = "", cta: str = "") -> Optional[bytes]:
        category = self._detect_category(prompt)

        # Для анонсов – сразу баннер (можно тоже попробовать HF, но пока оставим баннер)
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
                return self._create_fallback_image()

        # Для постов – пробуем генераторы по очереди
        detailed_prompt = self._build_detailed_prompt(prompt)
        for name, gen in self.generators:
            try:
                logger.info(f"Попытка генерации через {name}")
                result = gen.generate(detailed_prompt)
                if result and isinstance(result, bytes) and len(result) > 0:
                    logger.info(f"✅ Успешно через {name}, размер {len(result)} байт")
                    return result
            except Exception as e:
                logger.error(f"{name} ошибка: {e}")

        # Если ничего не сработало – баннер-заглушка
        logger.warning("Все генераторы не сработали, создаём баннер-заглушку")
        try:
            return self.banner_generator.create_banner(
                title=prompt[:50],
                subtitle="Подробности в посте",
                cta="ЧИТАТЬ",
                category=category
            )
        except Exception as e:
            logger.error(f"Ошибка баннера-заглушки: {e}")
            return self._create_fallback_image()

    # Остальные методы (detect_category, build_detailed_prompt, fallback) – как раньше
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