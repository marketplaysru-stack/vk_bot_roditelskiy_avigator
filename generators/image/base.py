from abc import ABC, abstractmethod
from typing import Optional

class ImageGenerator(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> Optional[bytes]:
        pass