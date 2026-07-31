"""
publishers/vk/publisher.py
---------------------------------------
Главный класс публикации в VK.
"""

from __future__ import annotations

from core.logger import get_logger

from models.group import Group
from models.post import Post
from models.publish_result import PublishResult

from publishers.formatter.manager import formatter_manager

from publishers.vk.api import VKApi
from publishers.vk.photos import VKPhotos
from publishers.vk.wall import VKWall


class VKPublisher:
    """
    Публикация постов ВКонтакте.
    """

    def __init__(self, token: str):

        self.logger = get_logger(self.__class__.__name__)

        self.api = VKApi(token)

        self.photos = VKPhotos(self.api)

        self.wall = VKWall(self.api)

    # ==================================================

    def publish(
        self,
        post: Post,
        group: Group,
    ) -> PublishResult:

        try:

            # ------------------------------------------
            # Форматирование поста
            # ------------------------------------------

            post = formatter_manager.format(
                post,
                group,
            )

            attachment = None

            # ------------------------------------------
            # Загрузка изображения
            # ------------------------------------------

            if post.image:

                attachment = self.photos.upload_photo(

                    group.group_id,

                    post.image,

                )

            # ------------------------------------------
            # Публикация
            # ------------------------------------------

            post_id = self.wall.post(

                group_id=group.group_id,

                message=post.text,

                attachments=attachment,

            )

            self.logger.info(

                "Пост успешно опубликован (%s)",

                post_id,

            )

            return PublishResult.success_result(

                provider="VK",

                post_id=str(post_id),

                message="Пост опубликован",

            )

        except Exception as exc:

            self.logger.exception(exc)

            return PublishResult.error_result(

                provider="VK",

                message=str(exc),

                exception=repr(exc),

            )