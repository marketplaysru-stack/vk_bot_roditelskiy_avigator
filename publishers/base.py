from abc import ABC, abstractmethod
from typing import Any

class Publisher(ABC):
    @abstractmethod
    def publish(self, post: Any, group: Any) -> Any:
        pass