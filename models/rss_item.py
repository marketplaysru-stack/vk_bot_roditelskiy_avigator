"""
models/rss_item.py
---------------------------------------
Модель RSS-записи.

Используется RSS Reader'ом и генераторами.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class RSSItem:
    """
    Универсальная модель RSS-новости.
    """

    # ==================================================
    # Основное
    # ==================================================

    title: str

    link: str

    description: str = ""

    content: str = ""

    author: str = ""

    category: str = ""

    language: str = "ru"

    # ==================================================
    # Источник
    # ==================================================

    source: str = ""

    feed_url: str = ""

    image: str | None = None

    # ==================================================
    # Дата
    # ==================================================

    published_at: datetime | None = None

    fetched_at: datetime = field(
        default_factory=datetime.now
    )

    # ==================================================
    # Состояние
    # ==================================================

    processed: bool = False

    hash: str = ""

    # ==================================================
    # Дополнительно
    # ==================================================

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # ==================================================

    @property
    def short_title(self):

        if len(self.title) < 80:
            return self.title

        return self.title[:77] + "..."

    # ==================================================

    @property
    def has_image(self):

        return self.image is not None

    # ==================================================

    def mark_processed(self):

        self.processed = True

    # ==================================================

    def to_dict(self):

        return {

            "title": self.title,

            "link": self.link,

            "description": self.description,

            "content": self.content,

            "author": self.author,

            "category": self.category,

            "language": self.language,

            "source": self.source,

            "feed_url": self.feed_url,

            "image": self.image,

            "published_at":
                self.published_at.isoformat()
                if self.published_at else None,

            "fetched_at":
                self.fetched_at.isoformat(),

            "processed": self.processed,

            "hash": self.hash,

            "metadata": self.metadata

        }

    # ==================================================

    @classmethod
    def from_dict(cls, data):

        published = data.get("published_at")

        fetched = data.get("fetched_at")

        return cls(

            title=data["title"],

            link=data["link"],

            description=data.get(
                "description",
                ""
            ),

            content=data.get(
                "content",
                ""
            ),

            author=data.get(
                "author",
                ""
            ),

            category=data.get(
                "category",
                ""
            ),

            language=data.get(
                "language",
                "ru"
            ),

            source=data.get(
                "source",
                ""
            ),

            feed_url=data.get(
                "feed_url",
                ""
            ),

            image=data.get(
                "image"
            ),

            published_at=(
                datetime.fromisoformat(published)
                if published else None
            ),

            fetched_at=(
                datetime.fromisoformat(fetched)
                if fetched else datetime.now()
            ),

            processed=data.get(
                "processed",
                False
            ),

            hash=data.get(
                "hash",
                ""
            ),

            metadata=data.get(
                "metadata",
                {}
            )

        )