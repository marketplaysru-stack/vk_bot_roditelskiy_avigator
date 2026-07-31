"""models/post.py"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Post:
    text: str
    image_url: Optional[str] = None
    image_bytes: Optional[bytes] = None