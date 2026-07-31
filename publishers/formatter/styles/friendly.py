"""
publishers/formatter/styles/friendly.py
---------------------------------------
Стиль оформления для родительских и семейных сообществ.
"""

from publishers.formatter.styles.default import DefaultFormatter


class FriendlyFormatter(DefaultFormatter):
    """
    Дружелюбный стиль оформления.
    """

    name = "friendly"

    title_prefix = "👨‍👩‍👧"

    footer = (
        "❤️ Если публикация была полезной — "
        "поделитесь ей с друзьями.\n"
        "💬 Будем рады вашему мнению в комментариях."
    )