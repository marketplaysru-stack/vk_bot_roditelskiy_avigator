"""
generators/image/picsum.py
---------------------------------------
Резервный генератор изображений.

Используется, если AI-генерация недоступна.
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from core.http import http

from generators.image.base import BaseImageGenerator


class PicsumGenerator(BaseImageGenerator):

    name = "picsum"

    def generate(
        self,
        prompt: str = "",
        output_dir: str = "data/images",
        width: int = 1024,
        height: int = 1024,
        **kwargs,
    ) -> Path:

        self.before_generate(prompt)

        output = Path(output_dir)
        output.mkdir(
            parents=True, exist_ok=True
        )

        filename = output / f"{uuid4().hex}.jpg"

        url = (
            f"https://picsum.photos/"
            f"{width}/{height}"
        )

        http.download(
            url,
            filename,
        )

        return self.after_generate(
            filename
        )