from abc import ABC, abstractmethod

class TextGenerator(ABC):
    @abstractmethod
    def generate(self, topic: str) -> str:
        pass

class ImageGenerator(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass