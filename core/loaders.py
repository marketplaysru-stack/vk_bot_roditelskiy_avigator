"""
core/loaders.py
---------------------------------------
Динамическая загрузка классов проекта.

Пример:

TEXT_GENERATOR_CLASS=generators.text.agnes:AgnesGenerator
IMAGE_GENERATOR_CLASS=generators.image.manager:ImageGeneratorManager
"""

from __future__ import annotations

import importlib

from core.exceptions import ConfigError
from core.logger import get_logger

logger = get_logger(__name__)


class ClassLoader:
    """
    Динамическая загрузка классов.

    Формат:

    package.module:ClassName
    """

    @staticmethod
    def load(path: str):

        if ":" not in path:

            raise ConfigError(
                f"Неверный путь класса: {path}"
            )

        module_name, class_name = path.split(":", 1)

        try:

            module = importlib.import_module(module_name)

        except Exception as e:

            raise ConfigError(
                f"Не удалось импортировать модуль {module_name}"
            ) from e

        try:

            cls = getattr(module, class_name)

        except AttributeError as e:

            raise ConfigError(
                f"Класс {class_name} отсутствует в {module_name}"
            ) from e

        logger.info(
            "Загружен класс %s",
            path
        )

        return cls

    @staticmethod
    def create(path: str, *args, **kwargs):
        """
        Создать экземпляр класса.
        """

        cls = ClassLoader.load(path)

        return cls(*args, **kwargs)


# =====================================================
# Вспомогательные функции
# =====================================================

def load_class(path: str):
    return ClassLoader.load(path)


def create_instance(path: str, *args, **kwargs):
    return ClassLoader.create(path, *args, **kwargs)