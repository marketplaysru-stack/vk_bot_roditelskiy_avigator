from dataclasses import dataclass
from typing import Optional

@dataclass
class Post:
    text: str
    image_url: Optional[str] = None

    def add_image(self, url: str):
        self.image_url = url