"""
publishers/formatter/styles/default.py
--------------------------------------
Стандартный стиль оформления публикации.
"""

from __future__ import annotations

from publishers.formatter.base import BaseFormatter

from models.group import Group
from models.post import Post


class DefaultFormatter(BaseFormatter):

    name = "default"

    separator = "\n\n────────────\n\n"

    footer = ""

    title_prefix = ""

    # ================================================

    def format(
        self,
        post: Post,
        group: Group,
    ) -> Post:

        blocks = []

        # ----------------------------------------
        # Заголовок
        # ----------------------------------------

        if post.title:

            if self.title_prefix:

                blocks.append(
                    f"{self.title_prefix} {post.title}"
                )

            else:

                blocks.append(post.title)

        # ----------------------------------------
        # Основной текст
        # ----------------------------------------

        if post.text:

            blocks.append(

                self.clean_text(post.text)

            )

        # ----------------------------------------
        # Хештеги
        # ----------------------------------------

        hashtags = self.build_hashtags(post)

        if hashtags:

            blocks.append(hashtags)

        # ----------------------------------------
        # Подвал
        # ----------------------------------------

        if self.footer:

            blocks.append(self.footer)

        # ----------------------------------------

        post.text = self.separator.join(blocks)

        return post