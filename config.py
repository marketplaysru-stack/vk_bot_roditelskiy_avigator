"""
config.py
------------------------------------
Единый модуль загрузки конфигурации проекта.

Загружает:
- .env
- data/groups.json

Использование:

from config import config

print(config.telegram_token)
print(config.groups)
print(config.rss_sources)
print(config.rss_default_group)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv
import os

# --------------------------------------------------
# Пути проекта
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

LOG_DIR = BASE_DIR / "logs"

CACHE_DIR = BASE_DIR / "cache"

GROUPS_FILE = DATA_DIR / "groups.json"

ENV_FILE = BASE_DIR / ".env"

# --------------------------------------------------
# Загрузка .env
# --------------------------------------------------

load_dotenv(ENV_FILE)

# --------------------------------------------------
# Логгер
# --------------------------------------------------

logger = logging.getLogger("config")

# --------------------------------------------------
# Dataclass группы
# --------------------------------------------------


@dataclass
class GroupConfig:
    name: str

    group_id: int

    vk_token: str

    enabled: bool = True

    style: str = "default"

    category: str = "general"


# --------------------------------------------------
# Основная конфигурация
# --------------------------------------------------


@dataclass
class Config:

    telegram_token: str

    agnes_api_key: str

    hf_token: str

    imgbb_api_key: str

    pollinations_url: str

    health_port: int = 8080

    timezone: str = "Europe/Tallinn"

    post_times: list = field(default_factory=lambda: [
        "07:00",
        "11:00",
        "13:00",
        "18:00"
    ])

    groups: Dict[str, GroupConfig] = field(default_factory=dict)

    # ========== RSS ==========
    rss_sources: list = field(default_factory=list)
    rss_default_group: str = "AI Навигатор"

    # ========== ЛИЧНАЯ СТРАНИЦА ==========
    vk_user_id: int = 0
    vk_token_user: str = ""


# --------------------------------------------------
# Загрузка групп
# --------------------------------------------------


def load_groups() -> Dict[str, GroupConfig]:

    groups = {}

    if not GROUPS_FILE.exists():

        logger.warning("groups.json не найден")

        return groups

    with open(GROUPS_FILE, "r", encoding="utf-8") as f:

        raw = json.load(f)

    for name, item in raw.items():

        groups[name] = GroupConfig(

            name=name,

            group_id=item["group_id"],

            vk_token=item["token"],

            enabled=item.get("enabled", True),

            style=item.get("style", "default"),

            category=item.get("category", "general"),

        )

    return groups


# --------------------------------------------------
# Проверка обязательных переменных
# --------------------------------------------------


def require(name: str) -> str:

    value = os.getenv(name)

    if not value:

        raise RuntimeError(

            f"Не найдена обязательная переменная окружения: {name}"

        )

    return value


# --------------------------------------------------
# Создание директорий
# --------------------------------------------------


def ensure_dirs():

    DATA_DIR.mkdir(exist_ok=True)

    LOG_DIR.mkdir(exist_ok=True)

    CACHE_DIR.mkdir(exist_ok=True)

    (CACHE_DIR / "images").mkdir(exist_ok=True)

    (CACHE_DIR / "rss").mkdir(exist_ok=True)

    (CACHE_DIR / "prompts").mkdir(exist_ok=True)


# --------------------------------------------------
# Загрузка конфигурации
# --------------------------------------------------


def load_config() -> Config:

    ensure_dirs()

    # Загружаем RSS-источники из .env (JSON-строка)
    rss_sources_json = os.getenv("RSS_SOURCES", "[]")
    try:
        rss_sources = json.loads(rss_sources_json)
    except json.JSONDecodeError:
        logger.warning("RSS_SOURCES не является корректным JSON, использую пустой список")
        rss_sources = []

    cfg = Config(

        telegram_token=require("TELEGRAM_TOKEN"),

        agnes_api_key=os.getenv("AGNES_API_KEY", ""),

        hf_token=os.getenv("HF_TOKEN", ""),

        imgbb_api_key=os.getenv("IMGBB_API_KEY", ""),

        pollinations_url=os.getenv(

            "POLLINATIONS_BASE_URL",

            "https://image.pollinations.ai"

        ),

        health_port=int(os.getenv("HEALTH_PORT", "8080")),

        timezone=os.getenv(

            "TIMEZONE",

            "Europe/Tallinn"

        ),

        groups=load_groups(),

        # ========== RSS ==========
        rss_sources=rss_sources,
        rss_default_group=os.getenv("RSS_DEFAULT_GROUP", "AI Навигатор"),

        # ========== ЛИЧНАЯ СТРАНИЦА ==========
        vk_user_id=int(os.getenv("VK_USER_ID", "0")),
        vk_token_user=os.getenv("VK_TOKEN_USER", ""),

    )

    logger.info(

        "Загружено групп: %s",

        len(cfg.groups)

    )

    logger.info(

        "Загружено RSS-источников: %s",

        len(cfg.rss_sources)

    )

    return cfg


# --------------------------------------------------
# Глобальный объект
# --------------------------------------------------

config = load_config()