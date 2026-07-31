"""generators/image/banner.py – профессиональные баннеры без прозрачности"""
import io
import random
from PIL import Image, ImageDraw, ImageFont

class BannerGenerator:
    def __init__(self):
        self.width = 1024
        self.height = 1024

    def create_banner(self, title: str = "", subtitle: str = "", cta: str = "", category: str = "general") -> bytes:
        theme = self._get_theme(category)

        # Основное изображение RGB
        img = Image.new('RGB', (self.width, self.height), color='#0a0a2e')
        draw = ImageDraw.Draw(img)

        # Градиент
        self._draw_gradient(draw, theme)

        # Оверлей (создаём отдельно, конвертируем в RGB и накладываем)
        overlay = Image.new('RGBA', (self.width, self.height), (0,0,0,0))
        overlay_draw = ImageDraw.Draw(overlay)
        for y in range(self.height//2, self.height):
            alpha = int(200 * (1 - (y - self.height//2) / (self.height//2)))
            overlay_draw.rectangle((0, y, self.width, y+1), fill=(0,0,0,alpha))
        # Накладываем оверлей как RGB
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)

        # Иконки
        self._draw_icons(draw, theme)

        # Текст
        self._draw_text(draw, title, subtitle, cta, theme)

        # Рамка
        self._draw_frame(draw, theme)

        # Сохраняем как JPEG (без прозрачности)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=95)
        return buf.getvalue()

    def _get_theme(self, category: str):
        themes = {
            "construction": {
                "colors": ['#FF8C00', '#1E90FF', '#FFD700', '#FFFFFF'],
                "icons": ['🏗️', '🚧', '📐', '🔧', '⚙️'],
                "gradient": ('#1a1a2e', '#16213e', '#0f3460')
            },
            "business": {
                "colors": ['#FFD700', '#003366', '#FFFFFF', '#00CED1'],
                "icons": ['📈', '💰', '🤝', '🎯', '💼'],
                "gradient": ('#0d1b2a', '#1b263b', '#415a77')
            },
            "ai": {
                "colors": ['#6A0DAD', '#00FFFF', '#FF00FF', '#FFFFFF'],
                "icons": ['🤖', '🧠', '⚡', '💡', '🌐'],
                "gradient": ('#0a0a2e', '#1a0a3e', '#2d1b69')
            },
            "education": {
                "colors": ['#008080', '#FFD700', '#FFFFFF', '#32CD32'],
                "icons": ['📚', '🎓', '✏️', '📝', '🧪'],
                "gradient": ('#0b2d2e', '#1a4a4b', '#2b6e6f')
            },
            "general": {
                "colors": ['#1E90FF', '#FFD700', '#FFFFFF', '#FF69B4'],
                "icons": ['⚙️', '📊', '💡', '🚀', '🎯'],
                "gradient": ('#0a0a2e', '#1a1a4e', '#2a2a6e')
            }
        }
        return themes.get(category, themes["general"])

    def _draw_gradient(self, draw, theme):
        c1 = self._hex_to_rgb(theme['gradient'][0])
        c2 = self._hex_to_rgb(theme['gradient'][1])
        c3 = self._hex_to_rgb(theme['gradient'][2])
        for y in range(self.height):
            ratio = y / self.height
            if ratio < 0.5:
                r = int(c1[0] + (c2[0] - c1[0]) * ratio * 2)
                g = int(c1[1] + (c2[1] - c1[1]) * ratio * 2)
                b = int(c1[2] + (c2[2] - c1[2]) * ratio * 2)
            else:
                r = int(c2[0] + (c3[0] - c2[0]) * (ratio - 0.5) * 2)
                g = int(c2[1] + (c3[1] - c2[1]) * (ratio - 0.5) * 2)
                b = int(c2[2] + (c3[2] - c2[2]) * (ratio - 0.5) * 2)
            draw.rectangle((0, y, self.width, y+1), fill=(r, g, b))

    def _draw_icons(self, draw, theme):
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 120)
        except:
            font = ImageFont.load_default()

        icons = theme['icons']
        positions = [
            (80, 80),
            (self.width-160, 80),
            (80, self.height-160),
            (self.width-160, self.height-160),
            (self.width//2-60, 60),
            (self.width//2-60, self.height-120)
        ]
        for pos in positions:
            icon = random.choice(icons)
            draw.text(pos, icon, fill='#FFFFFF80', font=font)

    def _draw_text(self, draw, title, subtitle, cta, theme):
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
            font_cta = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            font_cta = ImageFont.load_default()

        y_offset = self.height - 150

        if title:
            bbox = draw.textbbox((0, 0), title, font=font_title)
            tw = bbox[2] - bbox[0]
            x = (self.width - tw) // 2
            draw.text((x+4, y_offset+4), title, fill='black', font=font_title)
            draw.text((x, y_offset), title, fill='white', font=font_title)
            y_offset -= 100

        if subtitle:
            bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
            tw = bbox[2] - bbox[0]
            x = (self.width - tw) // 2
            draw.text((x+2, y_offset+2), subtitle, fill='black', font=font_sub)
            draw.text((x, y_offset), subtitle, fill='#FFD700', font=font_sub)
            y_offset -= 90

        if cta:
            bbox = draw.textbbox((0, 0), cta, font=font_cta)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            x = (self.width - tw) // 2
            draw.rectangle((x-40, y_offset-30, x+tw+40, y_offset+th+30), fill='#FFD700', outline=None)
            draw.text((x, y_offset), cta, fill='#0a0a2e', font=font_cta)

        try:
            logo_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 35)
            draw.text((30, 30), "AI Навигатор", fill='white', font=logo_font)
        except:
            pass

    def _draw_frame(self, draw, theme):
        color = theme['colors'][1]
        draw.rectangle((10, 10, self.width-10, self.height-10), outline=color, width=8)

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0,2,4))