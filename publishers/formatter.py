"""
publishers/formatter.py
---------------------------------------
Форматирование публикаций перед отправкой.
"""

from __future__ import annotations

from models.group import Group
from models.post import Post


class PostFormatter:
    """
    Универсальный форматтер публикаций.

    Подготавливает Post к публикации
    в зависимости от группы.
    """

    SEPARATOR = "\n\n────────────\n\n"

    def format(
        self,
        post: Post,
        group: Group,
    ) -> Post:

        formatter = getattr(
            self,
            f"_style_{group.style}",
            self._style_default
        )

        return formatter(post, group)

    # ==================================================
    # DEFAULT
    # ==================================================

    def _style_default(
        self,
        post: Post,
        group: Group,
    ) -> Post:

        parts = []

        if post.title:
            parts.append(f"📌 {post.title}")

        if post.text:
            parts.append(post.text)

        if post.tags:
            parts.append(
                " ".join(
                    f"#{tag}" for tag in post.tags
                )
            )

        post.text = self.SEPARATOR.join(parts)

        return post

    # ==================================================
    # AI
    # ==================================================

    def _style_tech(
        self,
        post: Post,
        group: Group,
    ) -> Post:

        parts = []

        if post.title:
            parts.append(f"🤖 {post.title}")

        parts.append(post.text)

        if post.tags:
            parts.append(
                " ".join(
                    f"#{tag}" for tag in post.tags
                )
            )

        parts.append(
            "💬 Как вы считаете?"
        )

        post.text = self.SEPARATOR.join(parts)

        return post

    # ==================================================
    # CONSTRUCTION
    # ==================================================

    def _style_expert(
        self,
        post: Post,
        group: Group,
    ) -> Post:

        parts = []

        if post.title:
            parts.append(f"🏗 {post.title}")

        parts.append(post.text)

        if post.tags:
            parts.append(
                " ".join(
                    f"#{tag}" for tag in post.tags
                )
            )

        parts.append(
            "✔ Сохраняйте, чтобы не потерять."
        )

        post.text = self.SEPARATOR.join(parts)

        return post

    # ==================================================
    # PARENTS
    # ==================================================

    def _style_friendly(
        self,
        post: Post,
        group: Group,
    ) -> Post:

        parts = []

        if post.title:
            parts.append(f"👨‍👩‍👧 {post.title}")

        parts.append(post.text)

        if post.tags:
            parts.append(
                " ".join(
                    f"#{tag}" for tag in post.tags
                )
            )

        parts.append(
            "❤️ Поделитесь этим постом с друзьями."
        )

        post.text = self.SEPARATOR.join(parts)

        return post


formatter = PostFormatter()