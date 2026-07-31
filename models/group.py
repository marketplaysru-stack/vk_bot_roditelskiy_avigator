"""
models/group.py
---------------------------------------
Модель группы (сообщества), в которую
публикуются посты.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Group:
    """
    Универсальная модель площадки публикации.
    """

    # ----------------------------------
    # Основное
    # ----------------------------------

    name: str

    group_id: int

    token: str

    # ----------------------------------
    # Настройки
    # ----------------------------------

    enabled: bool = True

    category: str = "general"

    style: str = "default"

    language: str = "ru"

    # ----------------------------------
    # Дополнительные параметры
    # ----------------------------------

    description: str = ""

    tags: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    # =====================================================

    @property
    def is_public(self) -> bool:
        """
        True — публичная страница
        False — группа
        """
        return self.group_id > 0

    @property
    def vk_owner_id(self) -> int:
        """
        Возвращает owner_id для VK API.
        Для групп VK требуется отрицательный ID.
        """
        if self.group_id < 0:
            return self.group_id

        return -self.group_id

    # =====================================================

    def add_tag(self, tag: str):

        if tag not in self.tags:
            self.tags.append(tag)

    # =====================================================

    def to_dict(self) -> dict:

        return {
            "name": self.name,
            "group_id": self.group_id,
            "token": self.token,
            "enabled": self.enabled,
            "category": self.category,
            "style": self.style,
            "language": self.language,
            "description": self.description,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    # =====================================================

    @classmethod
    def from_dict(cls, data: dict):

        return cls(
            name=data["name"],
            group_id=data["group_id"],
            token=data["token"],
            enabled=data.get("enabled", True),
            category=data.get("category", "general"),
            style=data.get("style", "default"),
            language=data.get("language", "ru"),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )