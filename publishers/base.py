"""
publishers/base.py
---------------------------------------
Базовый класс для всех издателей.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.logger import get_logger
from models.group import Group
from models.post import Post
from models.publish_result import PublishResult


class BasePublisher(ABC):
    """
    Базовый издатель.

    Любой Publisher обязан реализовать метод publish().
    """

    platform = "Unknown"

    def __init__(self):

        self.logger = get_logger(self.__class__.__name__)

    # -------------------------------------------------

    @abstractmethod
    def publish(
        self,
        post: Post,
        group: Group,
    ) -> PublishResult:
        """
        Публикация поста.
        """
        raise NotImplementedError

    # -------------------------------------------------

    def before_publish(
        self,
        post: Post,
        group: Group,
    ):

        self.logger.info(
            "Подготовка публикации '%s' → %s",
            post.title or post.topic,
            group.name,
        )

    # -------------------------------------------------

    def after_publish(
        self,
        result: PublishResult,
    ):

        if result.ok:

            self.logger.info(
                "Публикация успешна (%s)",
                result.platform,
            )

        else:

            self.logger.error(
                "Ошибка публикации: %s",
                result.error,
            )