#!/usr/bin/env python3
"""
bot.py – Telegram-бот для управления публикациями в VK
Заменяет консольную версию. Запускает long polling для приёма команд.
"""

import time
import logging
from config import config
from core.logger import get_logger
from services.telegram import TelegramClient
from handlers.command_handler import CommandHandler

logger = get_logger("BOT")

def main():
    logger.info("🚀 Запуск Telegram-бота")

    if not config.telegram_token:
        logger.error("TELEGRAM_TOKEN не задан в .env")
        return

    client = TelegramClient(config.telegram_token)
    handler = CommandHandler()

    last_update_id = 0

    while True:
        try:
            updates = client.get_updates(offset=last_update_id + 1)
            if updates:
                logger.info(f"📩 Получено {len(updates)} обновлений")
                for update in updates:
                    last_update_id = update["update_id"]
                    if "message" in update:
                        msg = update["message"]
                        chat_id = msg["chat"]["id"]
                        if "text" in msg:
                            text = msg["text"].strip()
                            if text:
                                response = handler.handle(chat_id, text)
                                if response:
                                    client.send_message(chat_id, response)
            else:
                time.sleep(1)
        except Exception as e:
            logger.error(f"Ошибка в цикле: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()