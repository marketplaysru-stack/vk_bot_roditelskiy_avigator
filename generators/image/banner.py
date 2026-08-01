"""generators/image/banner.py – профессиональные баннеры с разнообразными макетами"""
import io
import random
from PIL import Image, ImageDraw, ImageFont

class BannerGenerator:
    def __init__(self):
        self.width = 1024
        self.height = 1024

    def create_banner(self, title: str = "", subtitle: str = "", cta: str = "", category: str = "general", is_announce: bool = False) -> bytes:
        # Выбираем случайный макет
        layout = random.choice(["gradient", "blocks", "minimal"])

        # Цветовая схема
        palette = self._get_palette(category)

        # Создаём изображение
        img = Image.new('RGB', (self.width, self.height), palette['bg'])
        draw = ImageDraw.Draw(img)

        if layout == "gradient":
            img = self._draw_gradient_banner(img, draw, palette, title, subtitle, cta, is_announce)
        elif layout == "blocks":
            img = self._draw_blocks_banner(img, draw, palette, title, subtitle, cta, is_announce)
        else:
            img = self._draw_minimal_banner(img, draw, palette, title, subtitle, cta, is_announce)

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()

    def _get_palette(self, category: str):
        palettes = {
            "construction": {
                'bg': '#0a1628',
                'accent1': '#FF8C00',
                'accent2': '#1E90FF',
                'accent3': '#FFD700',
                'text': '#FFFFFF',
                'cta_bg': '#FF8C00',
                'cta_text': '#0a1628'
            },
            "business": {
                'bg': '#0d1b2a',
                'accent1': '#FFD700',
                'accent2': '#00CED1',
                'accent3': '#FFFFFF',
                'text': '#FFFFFF',
                'cta_bg': '#FFD700',
                'cta_text': '#0d1b2a'
            },
            "ai": {
                'bg': '#0a0a2e',
                'accent1': '#6A0DAD',
                'accent2': '#00FFFF',
                'accent3': '#FF00FF',
                'text': '#FFFFFF',
                'cta_bg': '#FFD700',
                'cta_text': '#0a0a2e'
            },
            "general": {
                'bg': '#0a0a2e',
                'accent1': '#1E90FF',
                'accent2': '#FFD700',
                'accent3': '#FF69B4',
                'text': '#FFFFFF',
                'cta_bg': '#FFD700',
                'cta_text': '#0a0a2e'
            }
        }
        return palettes.get(category, palettes["general"])

    def _draw_gradient_banner(self, img, draw, palette, title, subtitle, cta, is_announce):
        # Рисуем градиент
        c1 = self._hex_to_rgb(palette['accent1'])
        c2 = self._hex_to_rgb(palette['accent2'])
        for y in range(self.height):
            ratio = y / self.height
            r = int(c1[0] + (c2[0] - c1[0]) * ratio)
            g = int(c1[1] + (c2[1] - c1[1]) * ratio)
            b = int(c1[2] + (c2[2] - c1[2]) * ratio)
            draw.rectangle((0, y, self.width, y+1), fill=(r, g, b))

        # Декоративные круги
        for _ in range(5):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            r = random.randint(50, 200)
            draw.ellipse((x-r, y-r, x+r, y+r), outline=palette['accent3'], width=3)

        # Текст
        self._draw_text(img, draw, palette, title, subtitle, cta, is_announce)
        return img

    def _draw_blocks_banner(self, img, draw, palette, title, subtitle, cta, is_announce):
        # Фон
        draw.rectangle((0, 0, self.width, self.height), fill=palette['bg'])

        # Цветной блок слева
        block_width = self.width // 3
        draw.rectangle((0, 0, block_width, self.height), fill=palette['accent1'])

        # Полупрозрачный блок справа
        overlay = Image.new('RGBA', (self.width, self.height), (0,0,0,0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle((block_width, 0, self.width, self.height), fill=(255,255,255,30))
        img.paste(overlay, (0,0), overlay)

        # Текст (сдвинут вправо)
        self._draw_text(img, draw, palette, title, subtitle, cta, is_announce, x_offset=block_width//2)
        return img

    def _draw_minimal_banner(self, img, draw, palette, title, subtitle, cta, is_announce):
        # Тёмный фон
        draw.rectangle((0, 0, self.width, self.height), fill=palette['bg'])

        # Рамка
        draw.rectangle((20, 20, self.width-20, self.height-20), outline=palette['accent2'], width=6)

        # Крупная иконка
        try:
            font_icon = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 200)
        except:
            font_icon = ImageFont.load_default()
        icons = ['🏗️', '📊', '🤖', '💡', '🚀']
        icon = random.choice(icons)
        draw.text((self.width//2-80, 200), icon, fill=palette['accent3'], font=font_icon)

        # Текст снизу
        self._draw_text(img, draw, palette, title, subtitle, cta, is_announce, y_offset=400)
        return img

    def _draw_text(self, img, draw, palette, title, subtitle, cta, is_announce, x_offset=0, y_offset=0):
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
            font_cta = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            font_cta = ImageFont.load_default()

        y_start = 400 + y_offset

        if title:
            bbox = draw.textbbox((0, 0), title, font=font_title)
            tw = bbox[2] - bbox[0]
            x = (self.width - tw) // 2 + x_offset
            draw.text((x+4, y_start+4), title, fill='black', font=font_title)
            draw.text((x, y_start), title, fill=palette['text'], font=font_title)
            y_start += 110

        if subtitle:
            bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
            tw = bbox[2] - bbox[0]
            x = (self.width - tw) // 2 + x_offset
            draw.text((x+2, y_start+2), subtitle, fill='black', font=font_sub)
            draw.text((x, y_start), subtitle, fill=palette['accent3'], font=font_sub)
            y_start += 90

        if cta:
            bbox = draw.textbbox((0, 0), cta, font=font_cta)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            x = (self.width - tw) // 2 + x_offset
            draw.rectangle((x-40, y_start-30, x+tw+40, y_start+th+30), fill=palette['cta_bg'], outline=None)
            draw.text((x, y_start), cta, fill=palette['cta_text'], font=font_cta)

        # Логотип
        try:
            logo_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 35)
            draw.text((30, 30), "AI Навигатор", fill='white', font=logo_font)
        except:
            pass

    def create_banner_from_image(self, image_bytes: bytes, title: str = "", subtitle: str = "", cta: str = "") -> bytes:
        # Оставляем старый метод для совместимости (накладывает текст на картинку)
        img = Image.open(io.BytesIO(image_bytes)).convert('RGBA')
        width, height = img.size
        draw = ImageDraw.Draw(img)

        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(height/14))
            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(height/20))
            font_cta = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(height/16))
        except:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            font_cta = ImageFont.load_default()

        overlay = Image.new('RGBA', (width, height), (0,0,0,0))
        overlay_draw = ImageDraw.Draw(overlay)
        for y in range(height//2, height):
            alpha = int(200 * (1 - (y - height//2) / (height//2)))
            overlay_draw.rectangle((0, y, width, y+1), fill=(0,0,0,alpha))
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)

        y_offset = height - 120
        if title:
            bbox = draw.textbbox((0, 0), title, font=font_title)
            tw = bbox[2] - bbox[0]
            x = (width - tw) // 2
            draw.text((x, y_offset), title, fill='white', font=font_title)
            y_offset -= int(height/12)

        if subtitle:
            bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
            tw = bbox[2] - bbox[0]
            x = (width - tw) // 2
            draw.text((x, y_offset), subtitle, fill='#FFD700', font=font_sub)
            y_offset -= int(height/15)

        if cta:
            bbox = draw.textbbox((0, 0), cta, font=font_cta)
            tw = bbox[2] - bbox[0]
            x = (width - tw) // 2
            draw.rectangle((x-30, y_offset-20, x+tw+30, y_offset+60), fill='#FFD700', outline=None)
            draw.text((x, y_offset), cta, fill='#0a0a2e', font=font_cta)

        rgb_img = img.convert('RGB')
        buf = io.BytesIO()
        rgb_img.save(buf, format='PNG')
        return buf.getvalue()

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0,2,4))