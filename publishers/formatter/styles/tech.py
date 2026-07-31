"""
publishers/formatter/styles/tech.py
--------------------------------------
Стиль оформления для AI и технологий.
"""

from publishers.formatter.styles.default import DefaultFormatter


class TechFormatter(DefaultFormatter):

    name = "tech"

    title_prefix = "🤖"

    footer = (
        "💬 Как вы считаете? "
        "Поделитесь мнением в комментариях."
    )