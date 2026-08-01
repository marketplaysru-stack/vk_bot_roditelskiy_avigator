"""generators/image/banner.py – создание баннеров и наложение текста"""
import io
import random
from PIL import Image, ImageDraw, ImageFont

class BannerGenerator:
    def __init__(self):
        self.width = 1024
        self.height = 1024

    def create_banner(self, title: str = "", subtitle: str = "", cta: str = "", category: str = "general", is_announce: bool = False) -> bytes:
        palette = self._get_palette(category)
        img = Image.new('RGB', (self.width, self.height), palette['bg'])
        draw = ImageDraw.Draw(img)

        # Случайный стиль
        style = random.choice(["gradient", "geometric", "minimal"])
        if style == "gradient":
            img = self._draw_gradient(img, draw, palette)
        elif style == "geometric":
            img = self._draw_geometric(img, draw, palette)
        else:
            img = self._draw_minimal(img, draw, palette)

        self._draw_text(img, draw, palette, title, subtitle, cta, is_announce)
        buf = io.BytesIO()
        img.save(buf, format='PNG', quality=95)
        return buf.getvalue()

    def _get_palette(self, category: str):
        palettes = {
            "construction": {
                'bg': '#0a1628', 'accent1': '#FF8C00', 'accent2': '#1E90FF',
                'accent3': '#FFD700', 'text': '#FFFFFF', 'cta_bg': '#FF8C00', 'cta_text': '#0a1628'
            },
            "business": {
                'bg': '#0d1b2a', 'accent1': '#FFD700', 'accent2': '#00CED1',
                'accent3': '#FFFFFF', 'text': '#FFFFFF', 'cta_bg': '#FFD700', 'cta_text': '#0d1b2a'
            },
            "ai": {
                'bg': '#0a0a2e', 'accent1': '#6A0DAD', 'accent2': '#00FFFF',
                'accent3': '#FF00FF', 'text': '#FFFFFF', 'cta_bg': '#FFD700', 'cta_text': '#0a0a2e'
            },
            "general": {
                'bg': '#0a0a2e', 'accent1': '#1E90FF', 'accent2': '#FFD700',
                'accent3': '#FF69B4', 'text': '#FFFFFF', 'cta_bg': '#FFD700', 'cta_text': '#0a0a2e'
            }
        }
        return palettes.get(category, palettes["general"])

    def _draw_gradient(self, img, draw, palette):
        c1 = self._hex_to_rgb(palette['bg'])
        c2 = self._hex_to_rgb(palette['accent1'])
        for y in range(img.height):
            ratio = y / img.height
            r = int(c1[0] + (c2[0] - c1[0]) * ratio)
            g = int(c1[1] + (c2[1] - c1[1]) * ratio)
            b = int(c1[2] + (c2[2] - c1[2]) * ratio)
            draw.rectangle((0, y, img.width, y+1), fill=(r, g, b))
        for _ in range(5):
            x = random.randint(0, img.width)
            y = random.randint(0, img.height)
            r = random.randint(50, 200)
            draw.ellipse((x-r, y-r, x+r, y+r), outline=palette['accent3'], width=4, fill=None)
        return img

    def _draw_geometric(self, img, draw, palette):
        draw.rectangle((0, 0, img.width, img.height), fill=palette['bg'])
        for i in range(0, img.width, 80):
            draw.line((i, 0, i, img.height), fill=palette['accent2'], width=2)
        for i in range(0, img.height, 80):
            draw.line((0, i, img.width, i), fill=palette['accent2'], width=2)
        for _ in range(4):
            x = random.randint(50, img.width-50)
            y = random.randint(50, img.height-50)
            r = random.randint(100, 250)
            draw.ellipse((x-r, y-r, x+r, y+r), outline=palette['accent1'], width=6, fill=None)
        return img

    def _draw_minimal(self, img, draw, palette):
        draw.rectangle((0, 0, img.width, img.height), fill=palette['bg'])
        try:
            font_icon = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 200)
        except:
            font_icon = ImageFont.load_default()
        icons = ['🏗️', '📊', '🤖', '💡', '🚀', '🎯', '💎', '⚡']
        icon = random.choice(icons)
        draw.text((img.width//2-80, 180), icon, fill=palette['accent3'], font=font_icon)
        return img

    def _draw_text(self, img, draw, palette, title, subtitle, cta, is_announce):
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
            font_cta = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            font_cta = ImageFont.load_default()

        y_start = 450

        if title:
            bbox = draw.textbbox((0, 0), title, font=font_title)
            tw = bbox[2] - bbox[0]
            x = (img.width - tw) // 2
            draw.text((x+4, y_start+4), title, fill='black', font=font_title)
            draw.text((x, y_start), title, fill=palette['text'], font=font_title)
            y_start += 110

        if subtitle:
            bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
            tw = bbox[2] - bbox[0]
            x = (img.width - tw) // 2
            draw.text((x+2, y_start+2), subtitle, fill='black', font=font_sub)
            draw.text((x, y_start), subtitle, fill=palette['accent3'], font=font_sub)
            y_start += 90

        if cta:
            bbox = draw.textbbox((0, 0), cta, font=font_cta)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            x = (img.width - tw) // 2
            draw.rectangle((x-40, y_start-30, x+tw+40, y_start+th+30), fill=palette['cta_bg'], outline=None)
            draw.text((x, y_start), cta, fill=palette['cta_text'], font=font_cta)

        try:
            logo_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 35)
            draw.text((30, 30), "AI Навигатор", fill='white', font=logo_font)
        except:
            pass

    def create_banner_from_image(self, image_bytes: bytes, title: str = "", subtitle: str = "", cta: str = "") -> bytes:
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