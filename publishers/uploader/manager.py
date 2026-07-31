"""
publishers/uploader/manager.py
---------------------------------------
Менеджер загрузчиков изображений.
"""

from __future__ import annotations

from pathlib import Path

from core.logger import get_logger

from models.group import Group
from models.upload_result import UploadResult

from publishers.uploader.base import BaseUploader


class UploaderManager:
    """
    Управляет всеми загрузчиками изображений.
    """

    def __init__(self):

        self.logger = get_logger(
            self.__class__.__name__
        )

        self._uploaders: dict[
            str,
            BaseUploader
        ] = {}

    # ==================================================

    def register(
        self,
        name: str,
        uploader: BaseUploader,
    ):

        """
        Регистрация нового загрузчика.
        """

        self._uploaders[name] = uploader

        self.logger.info(

            "Зарегистрирован uploader: %s",

            name

        )

    # ==================================================

    def get(
        self,
        name: str,
    ) -> BaseUploader | None:

        return self._uploaders.get(name)

    # ==================================================

    def upload(
        self,
        image: str | Path,
        group: Group,
        provider: str,
        **kwargs,
    ) -> UploadResult:

        uploader = self.get(provider)

        if uploader is None:

            return UploadResult.error_result(

                provider=provider,

                message=f"Uploader '{provider}' не найден."

            )

        return uploader.upload(

            image=image,

            group=group,

            **kwargs,

        )

    # ==================================================

    @property
    def providers(self):

        return sorted(

            self._uploaders.keys()

        )


uploader_manager = UploaderManager()