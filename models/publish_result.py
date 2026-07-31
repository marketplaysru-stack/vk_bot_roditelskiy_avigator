from dataclasses import dataclass
from typing import Optional

@dataclass
class PublishResult:
    ok: bool
    post_id: Optional[int] = None
    message: str = ""