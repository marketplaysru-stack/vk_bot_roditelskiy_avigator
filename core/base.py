"""
core/base.py
---------------------------------------
Базовые классы проекта.

Все генераторы, сервисы и публикации
наследуются отсюда.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from core.logger import get_logger


# =====================================================
# БАЗОВЫЙ КЛАСС
# =====================================================

class BaseModule(ABC):
    """
    Родитель всех компонентов проекта.
    """

    def __init__(self):

        self.logger = get_logger(self.__class__.__name__)

    @property
    def name(self):

        return self.__class__.__name__


# =====================================================
# TEXT GENERATOR
# =====================================================

class BaseTextGenerator(BaseModule):

    @abstractmethod
    def generate(
        self,
        topic: str,
        **kwargs
    ) -> str:
        """
        Возвращает текст.
        """
        raise NotImplementedError


# =====================================================
# IMAGE GENERATOR
# =====================================================

class BaseImageGenerator(BaseModule):

    @abstractmethod
    def generate(
        self,
        prompt: str,
        output_path: str | None = None,
        **kwargs
    ) -> str:
        """
        Возвращает путь к изображению.
        """
        raise NotImplementedError


# =====================================================
# PUBLISHER
# =====================================================

class BasePublisher(BaseModule):

    @abstractmethod
    def publish(
        self,
        text: str,
        image: str | None = None,
        **kwargs
    ):
        """
        Публикация.
        """
        raise NotImplementedError


# =====================================================
# SERVICE
# =====================================================

class BaseService(BaseModule):

    @abstractmethod
    def run(self):
        """
        Запуск сервиса.
        """
        raise NotImplementedError


# =====================================================
# HEALTH CHECK
# =====================================================

class BaseHealthCheck(BaseModule):

    @abstractmethod
    def check(self) -> bool:
        """
        Проверка состояния.
        """
        raise NotImplementedError


# =====================================================
# STORAGE
# =====================================================

class BaseStorage(BaseModule):

    @abstractmethod
    def load(self, *args, **kwargs):

        raise NotImplementedError

    @abstractmethod
    def save(self, *args, **kwargs):

        raise NotImplementedError


# =====================================================
# AI PROVIDER
# =====================================================

class BaseAIProvider(BaseModule):

    @abstractmethod
    def request(
        self,
        prompt: str,
        **kwargs
    ) -> Any:

        raise NotImplementedError