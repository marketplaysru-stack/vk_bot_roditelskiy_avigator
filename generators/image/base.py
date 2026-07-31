"""
generators/image/base.py
---------------------------------------
Базовый класс генераторов изображений.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from core.logger import get_logger


class BaseImageGenerator(ABC):
    """
    Базовый класс генераторов изображений.
    """

    name = "base"

    def __init__(self):

        self.logger = get_logger(
            self.__class__.__name__
        )

    # ==================================================

    @abstractmethod
    def generate(
        self,
        prompt: str,
        output_dir: str = "data/images",
        **kwargs,
    ) -> Path:
        """
        Генерирует изображение и
        возвращает путь к файлу.
        """
        raise NotImplementedError

    # ==================================================

    def before_generate(
        self,
        prompt: str,
    ):

        self.logger.info(

            "Генерация изображения: %s",

            prompt,

        )

    # ==================================================

    def after_generate(
        self,
        image: Path,
    ) -> Path:

        self.logger.info(

            "Изображение сохранено: %s",

            image,

        )

        return image