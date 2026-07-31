"""
models/publish_result.py
---------------------------------------
Результат публикации поста.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class PublishResult:
    """
    Универсальный результат публикации.
    """

    # -----------------------------------
    # Статус
    # -----------------------------------

    success: bool = False

    message: str = ""

    # -----------------------------------
    # Площадка
    # -----------------------------------

    platform: str = ""

    group: str = ""

    # -----------------------------------
    # Идентификаторы
    # -----------------------------------

    post_id: int | None = None

    owner_id: int | None = None

    url: str = ""

    # -----------------------------------
    # Ошибки
    # -----------------------------------

    error_code: int | None = None

    error: str = ""

    exception: str = ""

    # -----------------------------------
    # Время
    # -----------------------------------

    created_at: datetime = field(
        default_factory=datetime.now
    )

    duration: float = 0.0

    # -----------------------------------
    # Дополнительно
    # -----------------------------------

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # ==================================================

    @property
    def ok(self) -> bool:
        return self.success

    @property
    def failed(self) -> bool:
        return not self.success

    # ==================================================

    @classmethod
    def success_result(
        cls,
        platform: str,
        group: str,
        post_id: int,
        owner_id: int,
        url: str = "",
        duration: float = 0.0,
    ):

        return cls(

            success=True,

            platform=platform,

            group=group,

            post_id=post_id,

            owner_id=owner_id,

            url=url,

            duration=duration,

            message="OK",
        )

    # ==================================================

    @classmethod
    def error_result(
        cls,
        platform: str,
        group: str,
        message: str,
        error_code: int | None = None,
        exception: str = "",
    ):

        return cls(

            success=False,

            platform=platform,

            group=group,

            message=message,

            error_code=error_code,

            error=message,

            exception=exception,
        )

    # ==================================================

    def to_dict(self):

        return {

            "success": self.success,

            "message": self.message,

            "platform": self.platform,

            "group": self.group,

            "post_id": self.post_id,

            "owner_id": self.owner_id,

            "url": self.url,

            "error_code": self.error_code,

            "error": self.error,

            "exception": self.exception,

            "created_at": self.created_at.isoformat(),

            "duration": self.duration,

            "metadata": self.metadata,

        }