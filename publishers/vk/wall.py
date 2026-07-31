"""
publishers/vk/wall.py
---------------------------------------
Публикация записей на стену VK.
"""

from __future__ import annotations

from core.logger import get_logger

from publishers.vk.api import VKApi


class VKWall:
    """
    Работа со стеной VK.
    """

    def __init__(self, api: VKApi):

        self.api = api

        self.logger = get_logger(self.__class__.__name__)

    # ==================================================

    def post(
        self,
        group_id: int,
        message: str,
        attachments: str | None = None,
        publish_date: int | None = None,
        from_group: int = 1,
    ) -> int:
        """
        Публикация записи на стену сообщества.

        Возвращает ID опубликованного поста.
        """

        params = {
            "owner_id": -abs(group_id),
            "from_group": from_group,
            "message": message,
        }

        if attachments:
            params["attachments"] = attachments

        if publish_date:
            params["publish_date"] = publish_date

        response = self.api.method(
            "wall.post",
            **params,
        )

        post_id = response["post_id"]

        self.logger.info(
            "Пост опубликован: %s",
            post_id,
        )

        return post_id

    # ==================================================

    def edit(
        self,
        group_id: int,
        post_id: int,
        message: str,
        attachments: str | None = None,
    ) -> bool:
        """
        Редактирование опубликованного поста.
        """

        params = {
            "owner_id": -abs(group_id),
            "post_id": post_id,
            "message": message,
        }

        if attachments:
            params["attachments"] = attachments

        self.api.method(
            "wall.edit",
            **params,
        )

        self.logger.info(
            "Пост обновлен: %s",
            post_id,
        )

        return True

    # ==================================================

    def delete(
        self,
        group_id: int,
        post_id: int,
    ) -> bool:
        """
        Удаление поста.
        """

        self.api.method(
            "wall.delete",
            owner_id=-abs(group_id),
            post_id=post_id,
        )

        self.logger.info(
            "Пост удален: %s",
            post_id,
        )

        return True