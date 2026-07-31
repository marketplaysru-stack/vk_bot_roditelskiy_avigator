"""
publishers/formatter/manager.py
---------------------------------------
Менеджер форматтеров.

Выбирает стиль оформления по настройкам группы.
"""

from __future__ import annotations

from models.group import Group
from models.post import Post

from publishers.formatter.styles.default import DefaultFormatter
from publishers.formatter.styles.tech import TechFormatter
from publishers.formatter.styles.expert import ExpertFormatter
from publishers.formatter.styles.friendly import FriendlyFormatter


class FormatterManager:
    """
    Управляет всеми доступными форматтерами.
    """

    def __init__(self):

        self._formatters = {

            "default": DefaultFormatter(),

            "tech": TechFormatter(),

            "expert": ExpertFormatter(),

            "friendly": FriendlyFormatter(),

        }

    # =====================================================

    def register(
        self,
        name: str,
        formatter,
    ):

        """
        Регистрация нового форматтера.
        """

        self._formatters[name] = formatter

    # =====================================================

    def get(
        self,
        style: str,
    ):

        """
        Возвращает форматтер по имени.
        """

        return self._formatters.get(

            style,

            self._formatters["default"]

        )

    # =====================================================

    def format(
        self,
        post: Post,
        group: Group,
    ) -> Post:

        formatter = self.get(

            group.style

        )

        return formatter.format(

            post,

            group

        )

    # =====================================================

    @property
    def styles(self):

        """
        Список зарегистрированных стилей.
        """

        return sorted(

            self._formatters.keys()

        )


formatter_manager = FormatterManager()