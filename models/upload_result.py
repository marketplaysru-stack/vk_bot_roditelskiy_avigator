"""
models/upload_result.py
---------------------------------------
Результат загрузки изображения.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class UploadResult:
    """
    Универсальный результат загрузки изображения.
    """

    # ==========================================
    # Статус
    # ==========================================

    success: bool = False

    message: str = ""

    # ==========================================
    # Источник
    # ==========================================

    provider: str = ""

    # ==========================================
    # Файл
    # ==========================================

    file_path: str = ""

    file_name: str = ""

    mime_type: str = ""

    size: int = 0

    width: int | None = None

    height: int | None = None

    # ==========================================
    # Результат
    # ==========================================

    url: str = ""

    upload_id: str = ""

    attachment: str = ""

    # ==========================================
    # Ошибки
    # ==========================================

    error_code: int | None = None

    error: str = ""

    exception: str = ""

    # ==========================================
    # Время
    # ==========================================

    created_at: datetime = field(
        default_factory=datetime.now
    )

    duration: float = 0.0

    # ==========================================
    # Дополнительные данные
    # ==========================================

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # =================================================

    @property
    def ok(self) -> bool:
        return self.success

    @property
    def failed(self) -> bool:
        return not self.success

    # =================================================

    @classmethod
    def success_result(
        cls,
        provider: str,
        url: str = "",
        upload_id: str = "",
        attachment: str = "",
        **kwargs,
    ):

        return cls(

            success=True,

            provider=provider,

            url=url,

            upload_id=upload_id,

            attachment=attachment,

            message="OK",

            **kwargs
        )

    # =================================================

    @classmethod
    def error_result(
        cls,
        provider: str,
        message: str,
        error_code: int | None = None,
        exception: str = "",
    ):

        return cls(

            success=False,

            provider=provider,

            message=message,

            error=message,

            error_code=error_code,

            exception=exception,
        )

    # =================================================

    def to_dict(self):

        return {

            "success": self.success,

            "message": self.message,

            "provider": self.provider,

            "file_path": self.file_path,

            "file_name": self.file_name,

            "mime_type": self.mime_type,

            "size": self.size,

            "width": self.width,

            "height": self.height,

            "url": self.url,

            "upload_id": self.upload_id,

            "attachment": self.attachment,

            "error_code": self.error_code,

            "error": self.error,

            "exception": self.exception,

            "created_at": self.created_at.isoformat(),

            "duration": self.duration,

            "metadata": self.metadata,
        }