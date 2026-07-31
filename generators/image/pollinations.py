"""
generators/image/pollinations.py
---------------------------------------
Генерация изображений через Pollinations.
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4
from urllib.parse import quote

from config import settings

from core.http import http

from generators.image.base import BaseImageGenerator


class PollinationsGenerator(BaseImageGenerator):

    name = "pollinations"

    def generate(
        self,
        prompt: str,
        output_dir: str = "data/images",
        width: int = 1024,
        height: int = 1024,
        model: str = "flux",
        **kwargs,
    ) -> Path:

        self.before_generate(prompt)

        output = Path(output_dir)
        output.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename = output / f"{uuid4().hex}.png"

        encoded_prompt = quote(prompt)

        url = (
            f"{settings.POLLINATIONS_BASE_URL}/prompt/"
            f"{encoded_prompt}"
            f"?width={width}"
            f"&height={height}"
            f"&model={model}"
        )

        http.download(
            url,
            filename,
        )

        return self.after_generate(
            filename
        )