"""
publishers/uploader/base.py
---------------------------------------
Базовый класс для загрузчиков изображений.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from core.logger import get_logger


class BaseUploader(ABC):
    """
    Базовый загрузчик изображений.

    Любой загрузчик должен вернуть ссылку
    или идентификатор загруженного изображения.
    """

    name = "base"

    def __init__(self):

        self.logger = get_logger(
            self.__class__.__name__
        )

    # ==================================================

    @abstractmethod
    def upload(
        self,
        image: str | Path,
        **kwargs,
    ):
        """
        Загружает изображение.

        Parameters
        ----------
        image
            Путь к файлу.

        Returns
        -------
        Любой объект результата.
        """

        raise NotImplementedError

    # ==================================================

    def exists(
        self,
        image: str | Path,
    ) -> bool:

        return Path(image).exists()

    # ==================================================

    def validate(
        self,
        image: str | Path,
    ):

        path = Path(image)

        if not path.exists():

            raise FileNotFoundError(path)

        if path.stat().st_size == 0:

            raise ValueError(
                "Файл изображения пуст."
            )

        return path

    # ==================================================

    def before_upload(
        self,
        image: str | Path,
    ):

        self.logger.info(

            "Загрузка изображения %s",

            image

        )

    # ==================================================

    def after_upload(
        self,
        result,
    ):

        self.logger.info(

            "Загрузка завершена"

        )

        return result