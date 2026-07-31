"""
generators/text/manager.py
---------------------------------------
Менеджер текстовых генераторов.
"""

from __future__ import annotations

from config import settings

from generators.text.agnes import AgnesGenerator


class TextGeneratorManager:
    """
    Менеджер текстовых генераторов.
    """

    def __init__(self):

        self._generators = {
            "agnes": AgnesGenerator(),
        }

    # ==================================================

    def get(self):

        provider = getattr(
            settings,
            "TEXT_PROVIDER",
            "agnes",
        ).lower()

        return self._generators.get(
            provider,
            self._generators["agnes"],
        )

    # ==================================================

    def generate(
        self,
        topic: str,
        **kwargs,
    ):

        generator = self.get()

        return generator.generate(
            topic,
            **kwargs,
        )


text_manager = TextGeneratorManager()