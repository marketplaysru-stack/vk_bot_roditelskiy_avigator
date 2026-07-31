"""scheduler.py – RSS-планировщик автоматических публикаций"""
import time
import random
import json
import logging
import feedparser
from datetime import datetime
from typing import List, Dict, Any
from threading import Thread

from config import config
from core.logger import get_logger
from generators.text.manager import text_manager
from generators.image.multi import multi_image
from publishers.vk.publisher import VKPublisher
from models.post import Post
from core.groups import groups as groups_manager

logger = get_logger("scheduler")

class RSSScheduler:
    def __init__(self):
        self.rss_sources = config.rss_sources
        self.post_times = config.post_times
        self.default_group = config.rss_default_group
        self.state_file = config.cache_dir / "rss_state.json"
        self._running = False

    def start(self):
        if self._running:
            return
        self._running = True
        thread = Thread(target=self._run, daemon=True)
        thread.start()
        logger.info("RSS-планировщик запущен")

    def _run(self):
        while self._running:
            try:
                now = datetime.now()
                today = now.strftime("%Y-%m-%d")
                for time_str in self.post_times:
                    target_hour, target_minute = map(int, time_str.split(':'))
                    if now.hour == target_hour and now.minute == target_minute and now.second < 5:
                        key = f"{today}_{time_str}"
                        if not self._already_published(key):
                            self._publish_from_all_sources()
                            self._mark_published(key)
                time.sleep(30)
            except Exception as e:
                logger.error(f"Ошибка в цикле планировщика: {e}")
                time.sleep(60)

    def _already_published(self, key: str) -> bool:
        state = self._load_state()
        return state.get(key, False)

    def _mark_published(self, key: str):
        state = self._load_state()
        state[key] = True
        self._save_state(state)

    def _load_state(self) -> Dict[str, Any]:
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                try:
                    return json.load(f)
                except:
                    return {}
        return {}

    def _save_state(self, state: Dict[str, Any]):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def _publish_from_all_sources(self):
        """Публикует по одному посту из каждого уникального target (группы)."""
        # Группируем источники по target
        sources_by_target: Dict[str, List[Dict]] = {}
        for src in self.rss_sources:
            target = src.get("target", self.default_group)
            sources_by_target.setdefault(target, []).append(src)

        if not sources_by_target:
            logger.warning("Нет RSS-источников")
            return

        for target_group_name, sources in sources_by_target.items():
            # Для каждой группы выбираем случайный источник из её списка
            source = random.choice(sources)
            url = source.get("url")
            if not url:
                continue

            try:
                feed = feedparser.parse(url)
                if not feed.entries:
                    logger.warning(f"RSS-лента {url} пуста")
                    continue

                entry = random.choice(feed.entries)
                title = entry.get("title", "").strip()
                if not title:
                    continue

                # Генерируем текст и картинку
                text = text_manager.generate(title)
                image_bytes = multi_image.generate(title)
                post = Post(text=text, image_bytes=image_bytes)

                group = groups_manager.get(target_group_name)
                if not group:
                    logger.error(f"Группа '{target_group_name}' не найдена")
                    continue

                publisher = VKPublisher(group.token)
                result = publisher.publish(post, group)
                logger.info(f"Автоматическая публикация в '{target_group_name}': {result}")

            except Exception as e:
                logger.error(f"Ошибка публикации в '{target_group_name}': {e}")