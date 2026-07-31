"""
models/post.py
---------------------------------------
Основная модель публикации.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Post:
    """
    Универсальная модель публикации.

    Используется всеми сервисами:
    RSS
    AI
    VK
    Telegram
    Планировщик
    Аналитика
    """

    # ----------------------------------
    # Основное
    # ----------------------------------

    title: str = ""

    text: str = ""

    topic: str = ""

    # ----------------------------------
    # Медиа
    # ----------------------------------

    image: str | None = None

    images: list[str] = field(default_factory=list)

    video: str | None = None

    # ----------------------------------
    # Источник
    # ----------------------------------

    source: str = ""

    source_url: str = ""

    author: str = ""

    # ----------------------------------
    # Группа
    # ----------------------------------

    group: str = ""

    category: str = ""

    style: str = ""

    # ----------------------------------
    # VK
    # ----------------------------------

    vk_post_id: int | None = None

    vk_url: str = ""

    # ----------------------------------
    # Метки
    # ----------------------------------

    tags: list[str] = field(default_factory=list)

    # ----------------------------------
    # Статусы
    # ----------------------------------

    published: bool = False

    scheduled: bool = False

    failed: bool = False

    # ----------------------------------
    # Время
    # ----------------------------------

    created_at: datetime = field(
        default_factory=datetime.now
    )

    publish_at: datetime | None = None

    published_at: datetime | None = None

    # ----------------------------------
    # Генерация
    # ----------------------------------

    text_generator: str = ""

    image_generator: str = ""

    prompt: str = ""

    # ----------------------------------
    # Дополнительные данные
    # ----------------------------------

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================

    @property
    def has_image(self) -> bool:
        return bool(self.image or self.images)

    @property
    def is_published(self) -> bool:
        return self.published

    @property
    def short_text(self) -> str:

        if len(self.text) <= 120:
            return self.text

        return self.text[:117] + "..."

    # =====================================================

    def add_image(self, path: str):

        self.images.append(path)

        if not self.image:
            self.image = path

    # =====================================================

    def add_tag(self, tag: str):

        if tag not in self.tags:
            self.tags.append(tag)

    # =====================================================

    def mark_published(
        self,
        post_id: int | None = None,
        url: str = ""
    ):

        self.published = True

        self.failed = False

        self.vk_post_id = post_id

        self.vk_url = url

        self.published_at = datetime.now()

    # =====================================================

    def mark_failed(self):

        self.failed = True

        self.published = False

    # =====================================================

    def to_dict(self):

        return {
            "title": self.title,
            "text": self.text,
            "topic": self.topic,
            "image": self.image,
            "images": self.images,
            "video": self.video,
            "source": self.source,
            "source_url": self.source_url,
            "author": self.author,
            "group": self.group,
            "category": self.category,
            "style": self.style,
            "vk_post_id": self.vk_post_id,
            "vk_url": self.vk_url,
            "tags": self.tags,
            "published": self.published,
            "scheduled": self.scheduled,
            "failed": self.failed,
            "created_at": self.created_at.isoformat(),
            "publish_at": self.publish_at.isoformat() if self.publish_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "text_generator": self.text_generator,
            "image_generator": self.image_generator,
            "prompt": self.prompt,
            "metadata": self.metadata,
        }

    # =====================================================

    @classmethod
    def from_dict(cls, data: dict):

        post = cls()

        for key, value in data.items():

            if hasattr(post, key):
                setattr(post, key, value)

        return post