"""generators/image/banner.py – генерация рекламных баннеров без внешних API"""
import io
import random
from PIL import Image, ImageDraw, ImageFont

class BannerGenerator:
    def __init__(self):
        self.width = 1024
        self.height = 1024

    def create_banner(self, title: str = "", subtitle: str = "", cta: str = "") -> bytes:
        # Создаём изображение
        img = Image.new('RGB', (self.width, self.height), color='#0a0a2e')
        draw = ImageDraw.Draw(img)

        # Градиентный фон
        self._draw_gradient(draw)

        # Геометрические фигуры
        self._draw_shapes(draw)

        # Иконки
        self._draw_icons(draw)

        # Эффект свечения
        self._draw_glows(draw)

        # Текст
        self._draw_text(draw, title, subtitle, cta)

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()

    # ... (остальные методы без изменений, они уже были)