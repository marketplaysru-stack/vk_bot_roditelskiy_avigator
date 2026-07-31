"""
publishers/formatter/base.py
---------------------------------------
Базовый форматтер публикаций.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.logger import get_logger

from models.group import Group
from models.post import Post


class BaseFormatter(ABC):
    """
    Базовый класс для всех стилей оформления.

    Любой стиль должен вернуть изменённый объект Post.
    """

    name = "base"

    def __init__(self):

        self.logger = get_logger(self.__class__.__name__)

    # ==================================================

    @abstractmethod
    def format(
        self,
        post: Post,
        group: Group,
    ) -> Post:
        """
        Форматирование публикации.
        """
        raise NotImplementedError

    # ==================================================

    def build_hashtags(
        self,
        post: Post,
    ) -> str:

        if not post.tags:
            return ""

        return " ".join(
            f"#{tag.strip().replace(' ', '_')}"
            for tag in post.tags
        )

    # ==================================================

    def append_footer(
        self,
        text: str,
        footer: str,
    ) -> str:

        if not footer:
            return text

        return f"{text}\n\n{footer}"

    # ==================================================

    def append_hashtags(
        self,
        text: str,
        post: Post,
    ) -> str:

        hashtags = self.build_hashtags(post)

        if not hashtags:
            return text

        return f"{text}\n\n{hashtags}"

    # ==================================================

    def clean_text(
        self,
        text: str,
    ) -> str:

        return "\n".join(

            line.rstrip()

            for line in text.splitlines()

        ).strip()