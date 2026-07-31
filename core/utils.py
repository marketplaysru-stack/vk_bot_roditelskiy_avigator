"""
core/utils.py
---------------------------------------
Общие вспомогательные функции проекта.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import string
import time
from pathlib import Path
from typing import Any


# =====================================================
# ФАЙЛЫ
# =====================================================

def ensure_dir(path: str | Path) -> Path:
    """
    Создать папку, если её нет.
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


# =====================================================
# JSON
# =====================================================

def load_json(file: str | Path, default=None):

    file = Path(file)

    if not file.exists():
        return default

    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(file: str | Path, data):

    file = Path(file)

    with open(file, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


# =====================================================
# HASH
# =====================================================

def md5(text: str) -> str:

    return hashlib.md5(
        text.encode("utf-8")
    ).hexdigest()


# =====================================================
# RANDOM
# =====================================================

def random_string(length: int = 12):

    alphabet = string.ascii_letters + string.digits

    return "".join(
        random.choice(alphabet)
        for _ in range(length)
    )


# =====================================================
# ИМЕНА ФАЙЛОВ
# =====================================================

def unique_filename(
    prefix="img",
    ext=".png"
):

    return (
        f"{prefix}_"
        f"{int(time.time())}_"
        f"{random_string(6)}"
        f"{ext}"
    )


# =====================================================
# ТЕКСТ
# =====================================================

def clean_text(text: str) -> str:

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def truncate(text: str, length: int):

    if len(text) <= length:
        return text

    return text[:length - 3] + "..."


# =====================================================
# URL
# =====================================================

def is_url(value: str):

    return value.startswith(
        (
            "http://",
            "https://"
        )
    )


# =====================================================
# RETRY
# =====================================================

def retry(
    func,
    retries=3,
    delay=2,
    *args,
    **kwargs
):

    last_error = None

    for _ in range(retries):

        try:

            return func(
                *args,
                **kwargs
            )

        except Exception as e:

            last_error = e

            time.sleep(delay)

    raise last_error


# =====================================================
# SIZE
# =====================================================

def human_size(size: int):

    for unit in (
        "B",
        "KB",
        "MB",
        "GB"
    ):

        if size < 1024:
            return f"{size:.1f} {unit}"

        size /= 1024

    return f"{size:.1f} TB"