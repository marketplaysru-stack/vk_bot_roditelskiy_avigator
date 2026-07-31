"""models/upload_result.py"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class UploadResult:
    success: bool
    url: Optional[str] = None
    error: str = ""