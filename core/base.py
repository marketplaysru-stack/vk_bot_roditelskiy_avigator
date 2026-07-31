"""core/base.py – базовые классы для генераторов"""
from abc import ABC, abstractmethod
from typing import Optional


class TextGenerator(ABC):
    """Абстрактный базовый класс для генерации текста."""
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass


class ImageGenerator(ABC):
    """Абстрактный базовый класс для генерации изображений."""
    @abstractmethod
    def generate(self, prompt: str, negative_prompt: str = "", **kwargs) -> Optional[bytes]:
        pass