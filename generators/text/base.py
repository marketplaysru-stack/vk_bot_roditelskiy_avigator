"""
generators/text/base.py
---------------------------------------
Базовый класс текстовых генераторов.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.logger import get_logger

from models.post import Post


class BaseTextGenerator(ABC):
    """
    Базовый класс для генерации текста.
    """

    name = "base"

    def __init__(self):

        self.logger = get_logger(self.__class__.__name__)

    # ==================================================

    @abstractmethod
    def generate(
        self,
        topic: str,
        **kwargs,
    ) -> Post:
        """
        Генерирует текст поста.

        Parameters
        ----------
        topic : str
            Тема публикации.

        Returns
        -------
        Post
            Готовый пост.
        """
        raise NotImplementedError

    # ==================================================

    def before_generate(
        self,
        topic: str,
    ):

        self.logger.info(
            "Генерация текста: %s",
            topic,
        )

    # ==================================================

    def after_generate(
        self,
        post: Post,
    ) -> Post:

        self.logger.info(
            "Текст успешно сгенерирован."
        )

        return post