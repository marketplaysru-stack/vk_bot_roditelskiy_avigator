"""generators/image/banner.py – генерация рекламных баннеров без внешних API"""
import io
import random
from PIL import Image, ImageDraw, ImageFont
from .base import ImageGenerator

class BannerGenerator(ImageGenerator):
    def __init__(self):
        self.width = 1024
        self.height = 1024

    def generate(self, prompt: str = "", title: str = "", subtitle: str = "", cta: str = "") -> bytes:
        return self.create_banner(title, subtitle, cta)

    def create_banner(self, title: str = "", subtitle: str = "", cta: str = "") -> bytes:
        # Выбираем случайную цветовую схему
        schemes = [
            {'bg': [(10,20,50), (30,10,60), (50,20,80)], 'accents': ['#FFD700', '#00BFFF', '#FF6B6B', '#7B68EE']},
            {'bg': [(20,10,40), (60,20,70), (90,30,80)], 'accents': ['#FF4500', '#32CD32', '#1E90FF', '#FFD700']},
            {'bg': [(5,15,30), (10,40,60), (20,60,80)], 'accents': ['#FF69B4', '#00FA9A', '#FFA500', '#8A2BE2']},
            {'bg': [(40,10,30), (70,20,50), (100,30,70)], 'accents': ['#00FFFF', '#FF1493', '#FFD700', '#7FFF00']}
        ]
        scheme = random.choice(schemes)

        img = Image.new('RGB', (self.width, self.height), color='#0a0a2e')
        draw = ImageDraw.Draw(img)

        # Градиент
        colors = scheme['bg']
        for y in range(self.height):
            ratio = y / self.height
            r = int(colors[0][0] + (colors[-1][0] - colors[0][0]) * ratio)
            g = int(colors[0][1] + (colors[-1][1] - colors[0][1]) * ratio)
            b = int(colors[0][2] + (colors[-1][2] - colors[0][2]) * ratio)
            draw.rectangle((0, y, self.width, y+1), fill=(r, g, b))

        # Фигуры
        for _ in range(8):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            r = random.randint(30, 150)
            color = random.choice(scheme['accents'])
            draw.ellipse((x-r, y-r, x+r, y+r), outline=color, width=3, fill=None)
            r2 = r // 3
            draw.ellipse((x-r2, y-r2, x+r2, y+r2), fill=color, outline=None)

        # Иконки
        icons = ['⚙️', '📊', '🤖', '💡', '🚀', '🎯', '💎', '⚡', '📈', '🧠', '🏗️', '📚', '💰', '🌐']
        try:
            font_icon = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 70)
        except:
            font_icon = ImageFont.load_default()
        positions = [
            (50, 50),
            (self.width-120, 50),
            (50, self.height-120),
            (self.width-120, self.height-120),
            (self.width//2-40, 80),
            (self.width//2-40, self.height-80)
        ]
        for pos in positions:
            icon = random.choice(icons)
            draw.text(pos, icon, fill='#FFFFFF', font=font_icon)

        # Текст
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45)
            font_cta = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 55)
        except:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            font_cta = ImageFont.load_default()

        # Оверлей
        overlay = Image.new('RGBA', (self.width, self.height), (0,0,0,0))
        overlay_draw = ImageDraw.Draw(overlay)
        for y in range(self.height//2, self.height):
            alpha = int(200 * (1 - (y - self.height//2) / (self.height//2)))
            overlay_draw.rectangle((0, y, self.width, y+1), fill=(0,0,0,alpha))
        draw.bitmap((0,0), overlay, fill=None)

        y_offset = self.height - 130
        if title:
            bbox = draw.textbbox((0, 0), title, font=font_title)
            tw = bbox[2] - bbox[0]
            x = (self.width - tw) // 2
            draw.text((x, y_offset), title, fill='white', font=font_title)
            y_offset -= 90

        if subtitle:
            bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
            tw = bbox[2] - bbox[0]
            x = (self.width - tw) // 2
            draw.text((x, y_offset), subtitle, fill='#FFD700', font=font_sub)
            y_offset -= 80

        if cta:
            bbox = draw.textbbox((0, 0), cta, font=font_cta)
            tw = bbox[2] - bbox[0]
            x = (self.width - tw) // 2
            draw.rectangle((x-30, y_offset-20, x+tw+30, y_offset+60), fill='#FFD700', outline=None)
            draw.text((x, y_offset), cta, fill='#0a0a2e', font=font_cta)

        # Логотип
        try:
            logo_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
            draw.text((30, 30), "AI Навигатор", fill='#FFFFFF', font=logo_font)
        except:
            pass

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()