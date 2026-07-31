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

    def _generate_only(self, topic: str) -> str:
        try:
            text = text_manager.generate(topic)
            safe_text = html.escape(text)
            return f"📝 Сгенерированный текст:\n\n{safe_text}"
        except Exception as e:
            logger.error(f"Ошибка генерации: {e}")
            return f"❌ Ошибка генерации: {e}"

    def _publish(self, group_name: str, topic: str) -> str:
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

            # 2) Генерация картинки
            logger.info(f"Генерация картинки для темы: {topic}")
            image_bytes = multi_image.generate(topic)
            image_url = None

            if image_bytes:
                logger.info(f"Картинка получена, размер {len(image_bytes)} байт")
                from publishers.uploader.imgbb import ImgbbUploader
                uploader = ImgbbUploader()
                upload_result = uploader.upload(image_bytes)
                if upload_result and upload_result.success and upload_result.url:
                    image_url = upload_result.url
                    logger.info(f"Картинка загружена на imgbb: {image_url}")
                else:
                    logger.error(f"Ошибка загрузки на imgbb: {upload_result.error if upload_result else 'неизвестная'}")
            else:
                logger.warning("Генератор не вернул байты картинки")

            # 3) Публикация
            post = Post(text=text, image_url=image_url)
            publisher = VKPublisher(group.token)
            result = publisher.publish(post, group)

            if result.ok:
                return f"✅ Пост опубликован в '{group_name}' (id: {result.post_id})"
            else:
                return f"❌ Ошибка публикации: {result.message}"
        except Exception as e:
            logger.error(f"Ошибка публикации: {e}")
            return f"❌ Ошибка: {e}"