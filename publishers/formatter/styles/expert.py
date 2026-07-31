"""
publishers/formatter/styles/expert.py
--------------------------------------
Стиль оформления для строительной тематики.
"""

from publishers.formatter.styles.default import DefaultFormatter


class ExpertFormatter(DefaultFormatter):
    """
    Стиль для строительных публикаций.
    """

    name = "expert"

    title_prefix = "🏗"

    footer = (
        "📌 Сохраните публикацию, чтобы не потерять.\n"
        "💬 Делитесь опытом в комментариях."
    )