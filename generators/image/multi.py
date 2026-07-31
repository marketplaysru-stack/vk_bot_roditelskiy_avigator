"""generators/image/multi.py"""
import random
import logging
from typing import Optional
from .base import ImageGenerator
from .picsum import PicsumGenerator
from .pollinations import PollinationsGenerator
from PIL import Image, ImageDraw, ImageFont
import io

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.generators = [
            PollinationsGenerator(),
            PicsumGenerator(),
        ]

    def generate(self, prompt: str) -> Optional[bytes]:
        # Всегда строим детальный промпт на основе темы (даже если промпт уже детальный)
        is_announce = "Анонс" in prompt
        prompt = self._build_detailed_prompt(prompt, is_announce)

        for gen in self.generators:
            try:
                logger.info(f"Попытка генерации через {gen.__class__.__name__} с промптом (первые 100 символов): {prompt[:100]}...")
                result = gen.generate(prompt)
                if result and isinstance(result, bytes) and len(result) > 0:
                    logger.info(f"Успешно, размер {len(result)} байт")
                    return result
                else:
                    logger.warning(f"Генератор вернул пустой результат")
            except Exception as e:
                logger.warning(f"{gen.__class__.__name__} не сработал: {e}")

        logger.info("Создаём локальную картинку-заглушку")
        return self._create_fallback_image()

    def _build_detailed_prompt(self, raw_prompt: str, is_announce: bool = False) -> str:
        # Извлекаем тему
        topic = raw_prompt
        if "Анонс" in topic:
            if ":" in topic:
                parts = topic.split(":", 1)
                if len(parts) > 1:
                    topic = parts[1].strip()
                else:
                    topic = parts[0].strip()
            if "—" in topic:
                topic = topic.split("—")[0].strip()
        if len(topic) < 5:
            topic = "technology and innovation"

        # Детальный шаблон (как в примере)
        templates = [
            # Шаблон 1: интерфейс с графиками и иконками
            lambda t: (
                f"Hyperrealistic cinematic photograph, vertical 9:16, minimalist wide shot, centred composition. "
                f"A modern workspace with a large 4K monitor showing a dashboard with charts, graphs, and icons about {t}. "
                f"The screen is surrounded by subtle, out-of-focus neural network patterns and data streams. "
                f"On the desk, there's a stylus, a notebook, and a coffee cup. "
                f"Lighting: soft ambient light from the monitor, warm golden accents. "
                f"Mood: professional, innovative, organized. "
                f"Color palette: dark blue, soft white, gold accents, vibrant chart colors. "
                f"Style: product photography, shallow depth of field (f/2.8), 8K, crisp details, no people, no faces, no text. "
                f"--ar 9:16 --style raw --s 700 --v 6.0"
            ),
            # Шаблон 2: логотип с нейросетевым фоном
            lambda t: (
                f"Hyperrealistic cinematic photograph, vertical 9:16, minimalist wide shot, centred composition. "
                f"A deep, rich midnight-blue background with subtle, out-of-focus neural network patterns and data streams drifting vertically like digital rain. "
                f"In the centre, a stylized glowing compass made of brushed gold and silver, with a neural network pattern inside the compass rose — symbolizing 'AI Навигатор'. "
                f"Below, a subtle glowing tagline: '{t}'. "
                f"Lighting: the compass emits a warm golden glow, soft cyan and violet accents. "
                f"Sensory details: brushed metal texture, luminous lines, tiny golden particles drifting slowly. "
                f"Mood: premium, trustworthy, inspiring. "
                f"Color palette: deep midnight blue, rich gold, soft silver, subtle cyan and violet accents. "
                f"Style: premium branding, Apple keynote aesthetic, shallow depth of field (f/2.8), 8K, fine grain, no people, no faces, no text. "
                f"--ar 9:16 --style raw --s 700 --v 6.0"
            ),
            # Шаблон 3: динамичный, с иконками и графиками
            lambda t: (
                f"Hyperrealistic cinematic photograph, vertical 9:16, minimalist wide shot, centred composition. "
                f"A futuristic holographic display floating in a dark room, showing interactive 3D charts, gears, and AI icons representing {t}. "
                f"The display emits a soft blue and violet glow. "
                f"Background: dark with subtle light streaks. "
                f"Lighting: volumetric light, bright from the hologram, warm ambient around. "
                f"Mood: innovative, powerful, futuristic. "
                f"Color palette: deep blue, cyan, violet, gold highlights. "
                f"Style: sci-fi product photography, shallow depth of field, 8K, crisp details, no people, no faces, no text. "
                f"--ar 9:16 --style raw --s 700 --v 6.0"
            ),
            # Шаблон 4: для анонса – более яркий, призывный
            lambda t: (
                f"Hyperrealistic cinematic photograph, vertical 9:16, minimalist wide shot, centred composition. "
                f"A bright, modern workspace with a large screen showing vibrant graphs and icons related to {t}. "
                f"On the screen, a glowing 'Subscribe' button and a notification badge. "
                f"The desk has a smartphone, a notebook, and a cup of coffee. "
                f"Lighting: warm natural light from a window, soft shadows. "
                f"Mood: energetic, welcoming, action-oriented. "
                f"Color palette: white, soft blue, warm gold, bright accents. "
                f"Style: lifestyle photography, shallow depth of field, 8K, crisp details, no people, no faces, no text. "
                f"--ar 9:16 --style raw --s 700 --v 6.0"
            )
        ]

        # Выбираем случайный шаблон (для анонса чаще четвёртый)
        if is_announce:
            template = templates[3] if random.random() < 0.6 else random.choice(templates)
        else:
            template = random.choice(templates[:3]) if random.random() < 0.7 else templates[3]

        return template(topic)

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
        except Exception as e:
            logger.error(f"Ошибка создания заглушки: {e}")
            return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9c\x63\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc\xccY\xe7\x00\x00\x00\x00IEND\xaeB`\x82'

multi_image = MultiImageGenerator()