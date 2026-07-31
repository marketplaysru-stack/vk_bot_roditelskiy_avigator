"""
core/logger.py
---------------------------------------
Единый логгер проекта.

Особенности:
- Цветной вывод в консоль
- Запись в файл
- Автоматическое создание папки logs
- Ротация логов (7 файлов)
- Один логгер для всего проекта

Использование:

from core.logger import get_logger

logger = get_logger(__name__)

logger.info("Запуск")
logger.warning("Предупреждение")
logger.error("Ошибка")
"""

from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import colorlog

# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "bot.log"

# --------------------------------------------------

LOG_LEVEL = logging.INFO

# --------------------------------------------------

_console_formatter = colorlog.ColoredFormatter(
    "%(log_color)s[%(asctime)s] "
    "%(levelname)-8s "
    "%(name)s → "
    "%(message)s",
    datefmt="%H:%M:%S",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)

# --------------------------------------------------

_file_formatter = logging.Formatter(
    "[%(asctime)s] "
    "%(levelname)-8s "
    "%(name)s "
    "%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# --------------------------------------------------

_console_handler = logging.StreamHandler()

_console_handler.setFormatter(_console_formatter)

_console_handler.setLevel(LOG_LEVEL)

# --------------------------------------------------

_file_handler = TimedRotatingFileHandler(
    LOG_FILE,
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8",
)

_file_handler.setFormatter(_file_formatter)

_file_handler.setLevel(LOG_LEVEL)

# --------------------------------------------------

_created = {}

# --------------------------------------------------


def get_logger(name: str) -> logging.Logger:
    """
    Возвращает готовый логгер.

    Если логгер уже существует —
    повторно обработчики не добавляются.
    """

    if name in _created:
        return _created[name]

    logger = logging.getLogger(name)

    logger.setLevel(LOG_LEVEL)

    logger.propagate = False

    if not logger.handlers:

        logger.addHandler(_console_handler)

        logger.addHandler(_file_handler)

    _created[name] = logger

    return logger