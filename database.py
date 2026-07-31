"""
database.py
-----------------------------------------
Универсальный слой хранения данных.

На текущем этапе используется JSON.
Позже можно заменить на SQLite/PostgreSQL
без изменения остального проекта.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from threading import Lock
from typing import Any

from config import DATA_DIR

logger = logging.getLogger("database")


class JsonDatabase:

    def __init__(self):

        self.lock = Lock()

        self.groups_file = DATA_DIR / "groups.json"

        self.schedule_file = DATA_DIR / "schedule.json"

        self.posts_file = DATA_DIR / "posts.json"

        self.settings_file = DATA_DIR / "settings.json"

        self._ensure_files()

    # -------------------------------------------------

    def _ensure_files(self):

        defaults = {
            self.groups_file: {},
            self.schedule_file: [],
            self.posts_file: [],
            self.settings_file: {}
        }

        for file, default in defaults.items():

            if not file.exists():

                with open(file, "w", encoding="utf-8") as f:

                    json.dump(
                        default,
                        f,
                        ensure_ascii=False,
                        indent=4
                    )

    # -------------------------------------------------

    def load(self, file: Path):

        with self.lock:

            try:

                with open(file, "r", encoding="utf-8") as f:

                    return json.load(f)

            except Exception as e:

                logger.exception(e)

                return None

    # -------------------------------------------------

    def save(self, file: Path, data):

        with self.lock:

            with open(file, "w", encoding="utf-8") as f:

                json.dump(
                    data,
                    f,
                    ensure_ascii=False,
                    indent=4
                )

    # =================================================
    # GROUPS
    # =================================================

    def get_groups(self):

        return self.load(self.groups_file)

    # =================================================
    # SCHEDULE
    # =================================================

    def get_schedule(self):

        return self.load(self.schedule_file)

    def save_schedule(self, schedule):

        self.save(self.schedule_file, schedule)

    def add_schedule(self, item):

        schedule = self.get_schedule()

        schedule.append(item)

        self.save_schedule(schedule)

    def clear_schedule(self):

        self.save_schedule([])

    # =================================================
    # POSTS
    # =================================================

    def get_posts(self):

        return self.load(self.posts_file)

    def save_posts(self, posts):

        self.save(self.posts_file, posts)

    def add_post(self, post):

        posts = self.get_posts()

        posts.append(post)

        self.save_posts(posts)

    def clear_posts(self):

        self.save_posts([])

    # =================================================
    # SETTINGS
    # =================================================

    def get_settings(self):

        return self.load(self.settings_file)

    def save_settings(self, settings):

        self.save(self.settings_file, settings)

    def set_setting(self, key: str, value: Any):

        settings = self.get_settings()

        settings[key] = value

        self.save_settings(settings)

    def get_setting(self, key: str, default=None):

        settings = self.get_settings()

        return settings.get(key, default)


# -----------------------------------------------------

db = JsonDatabase()