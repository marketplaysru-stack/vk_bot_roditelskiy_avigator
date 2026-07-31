"""handlers/command_handler.py"""
import re
import logging
import html
from typing import Optional
from core.groups import groups as groups_manager
from generators.text.manager import text_manager
from generators.image.multi import multi_image
from publishers.vk.publisher import VKPublisher
from models.post import Post
from core.logger import get_logger
from config import config

logger = get_logger("command_handler")

class CommandHandler:
    def __init__(self):
        self.groups = groups_manager

    def handle(self, chat_id: int, text: str) -> Optional[str]:
        if not text:
            return None

        if text in ("/start", "/help"):
            return self._help()

        if text == "/list":
            return self._list_groups()

        if text == "/rss":
            return self._show_rss()

        match = re.match(r'/post\s+"([^"]+)"\s+(.+)', text)
        if match:
            group_name = match.group(1)
            topic = match.group(2)
            return self._publish(group_name, topic)

        match = re.match(r'/generate\s+(.+)', text)
        if match:
            topic = match.group(1)
            return self._generate_only(topic)

        return "❓ Неизвестная команда. Напишите /help"

    def _help(self) -> str:
        return (
            "🤖 AI Навигатор – управляющий бот\n\n"
            "Доступные команды:\n"
            "/list – показать все группы\n"
            "/rss – показать RSS-источники\n"
            "/generate <тема> – сгенерировать пост без публикации\n"
            "/post \"<группа>\" <тема> – сгенерировать и опубликовать\n\n"
            "Пример:\n"
            "/post \"AI Навигатор\" Нейросети в образовании"
        )

    def _list_groups(self) -> str:
        all_groups = self.groups.all()
        if not all_groups:
            return "📭 Нет доступных групп"
        lines = ["📋 Группы:"]
        for g in all_groups:
            lines.append(f"• {g.name} (ID: {g.group_id})")
        return "\n".join(lines)

    def _show_rss(self) -> str:
        if not config.rss_sources:
            return "📭 Нет настроенных RSS-источников"
        lines = ["📡 RSS-источники:"]
        for src in config.rss_sources:
            url = src.get("url", "нет URL")
            target = src.get("target", "не указан")
            lines.append(f"• {target} → {url}")
        return "\n".join(lines)

    def _generate_only(self, topic: str) -> str:
        try:
            text = text_manager.generate(topic)
            safe_text = html.escape(text)
            return f"📝 Сгенерированный текст:\n\n{safe_text}"
        except Exception as e:
            logger.error(f"Ошибка генерации: {e}")
            return f"❌ Ошибка генерации: {e}"

    def _publish(self, group_name: str, topic: str) -> str:
        # Логируем состояние конфига для анонса
        logger.info(f"VK_USER_ID: {config.vk_user_id}, VK_TOKEN_USER: {'*' * len(config.vk_token_user) if config.vk_token_user else 'empty'}")

        group = self.groups.get(group_name)
        if not group:
            return f"❌ Группа '{group_name}' не найдена. Используйте /list"

        try:
            # 1) Генерация текста
            logger.info(f"Генерация текста для темы: {topic}")
            text = text_manager.generate(topic)
            if not text:
                return "❌ Не удалось сгенерировать текст"
            logger.info(f"Текст сгенерирован (длина {len(text)})")

            # 2) Генерация баннера для поста (без кнопки, но с темой)
            logger.info(f"Генерация баннера для поста")
            image_bytes = multi_image.generate(
                topic,
                is_announce=False,
                title=topic[:50],
                subtitle="Подробности в нашем посте",
                cta="ЧИТАТЬ"
            )
            if image_bytes:
                logger.info(f"Баннер для поста получен, размер {len(image_bytes)} байт")
            else:
                logger.warning("Не удалось сгенерировать баннер для поста")

            # 3) Публикация в группу
            post = Post(text=text, image_bytes=image_bytes)
            publisher = VKPublisher(group.token)
            result = publisher.publish(post, group)

            if not result.ok:
                return f"❌ Ошибка публикации: {result.message}"

            group_link = f"https://vk.com/club{abs(group.group_id)}"

            # 4) Анонс на личную страницу (с баннером с кнопкой)
            if config.vk_user_id and config.vk_token_user:
                logger.info("Начинаем создание анонса на личную страницу")
                try:
                    announce_text = text_manager.generate_announce(topic, group_name)

                    # Генерируем баннер для анонса (с кнопкой подписки)
                    announce_image = multi_image.generate(
                        f"Анонс: {topic} — подпишись на {group_name}",
                        is_announce=True,
                        title="🔥 НОВОСТЬ",
                        subtitle=topic[:60] if len(topic) > 60 else topic,
                        cta="ПОДПИСЫВАЙСЯ"
                    )
                    user_publisher = VKPublisher(config.vk_token_user)
                    user_result = user_publisher.publish_to_user(announce_text, announce_image, group_link)
                    if user_result.ok:
                        logger.info(f"Анонс на личную страницу опубликован (id: {user_result.post_id})")
                    else:
                        logger.error(f"Ошибка публикации анонса: {user_result.message}")
                except Exception as e:
                    logger.error(f"Ошибка при создании анонса: {e}")
            else:
                logger.warning("Анонс на личную страницу не настроен (нет VK_USER_ID или VK_TOKEN_USER)")

            return f"✅ Пост опубликован в '{group_name}' (id: {result.post_id})"

        except Exception as e:
            logger.error(f"Ошибка публикации: {e}")
            return f"❌ Ошибка: {e}"