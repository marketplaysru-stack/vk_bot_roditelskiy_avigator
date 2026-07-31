from abc import ABC, abstractmethod

class TextGenerator(ABC):
    @abstractmethod
    def generate(self, topic: str) -> str:
        pass