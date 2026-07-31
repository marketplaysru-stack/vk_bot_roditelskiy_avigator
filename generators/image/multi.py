"""
generators/image/multi.py
---------------------------------------
Менеджер генерации изображений.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from core.logger import get_logger

from generators.image.pollinations import PollinationsGenerator
from generators.image.picsum import PicsumGenerator


class MultiImageGenerator:

    def __init__(self):

        self.logger = get_logger(self.__class__.__name__)

        self.pollinations = PollinationsGenerator()

        self.picsum = PicsumGenerator()

    # ==================================================

    def generate(
        self,
        prompt: str,
    ) -> Path:

        # ----------------------------------------------
        # Pollinations
        # ----------------------------------------------

        for attempt in range(3):

            try:

                self.logger.info(

                    "Pollinations (%s/3)",

                    attempt + 1,

                )

                return self.pollinations.generate(
                    prompt
                )

            except Exception as exc:

                self.logger.warning(exc)

        # ----------------------------------------------
        # Picsum
        # ----------------------------------------------

        try:

            self.logger.info(

                "Переход на Picsum"

            )

            return self.picsum.generate(
                prompt
            )

        except Exception as exc:

            self.logger.warning(exc)

        # ----------------------------------------------
        # Заглушка
        # ----------------------------------------------

        self.logger.warning(

            "Создание локальной картинки"

        )

        return self.create_placeholder(
            prompt
        )

    # ==================================================

    def create_placeholder(
        self,
        text: str,
    ) -> Path:

        output = Path("data/images")

        output.mkdir(
            parents=True,
            exist_ok=True,
        )

        file = output / "placeholder.png"

        image = Image.new(

            "RGB",

            (1024, 1024),

            (240, 240, 240),

        )

        draw = ImageDraw.Draw(image)

        try:

            font = ImageFont.truetype(

                "arial.ttf",

                32,

            )

        except Exception:

            font = ImageFont.load_default()

        draw.multiline_text(

            (40, 40),

            text,

            fill="black",

            font=font,

        )

        image.save(file)

        return file


multi_image = MultiImageGenerator()