#!/usr/bin/env python3
import os
import sys
import time
import json
import logging
import threading
import random
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional, Dict, Any, List
from io import BytesIO

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("bot")

# ========== КОНФИГУРАЦИЯ ==========
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN не задан")
    sys.exit(1)

VK_TOKEN_AI = os.getenv("VK_TOKEN_AI")
GROUP_ID_AI = int(os.getenv("GROUP_ID_AI", "0"))

AGNES_API_KEY = os.getenv("AGNES_API_KEY")
GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

IMAGE_NEGATIVE_PROMPT = os.getenv("IMAGE_NEGATIVE_PROMPT", "ugly, deformed, blurry, low quality, same face, boring, plain, cartoon, doll, mannequin, 3d render, smooth skin, unrealistic, extra limbs, bad anatomy, distorted, people, human, woman, girl, beach, sea, sand, swimsuit, nude, naked, portrait, selfie, smile, face, eyes, hair, meadow, field, hay, grass, farm, cow, horse, rural, village, landscape")
IMAGE_SEED_RANDOM = os.getenv("IMAGE_SEED_RANDOM", "true").lower() == "true"
IMAGE_CFG_SCALE = float(os.getenv("IMAGE_CFG_SCALE", "7.0"))
IMAGE_STEPS = int(os.getenv("IMAGE_STEPS", "30"))
IMAGE_WIDTH = int(os.getenv("IMAGE_WIDTH", "1024"))
IMAGE_HEIGHT = int(os.getenv("IMAGE_HEIGHT", "1024"))
HEALTH_PORT = int(os.getenv("HEALTH_PORT", "8080"))

RSS_DEFAULT_GROUP = os.getenv("RSS_DEFAULT_GROUP", "Родительский")
RSS_SOURCES_JSON = os.getenv("RSS_SOURCES", "[]")
try:
    RSS_SOURCES = json.loads(RSS_SOURCES_JSON)
except:
    RSS_SOURCES = []

DATA_DIR = Path("/data") if os.path.exists("/data") else Path("./data")
DATA_DIR.mkdir(exist_ok=True)
SCHEDULE_FILE = DATA_DIR / "schedule.json"
GROUPS_FILE = DATA_DIR / "groups.json"

import vk_api
from vk_api.utils import get_random_id
from vk_api.upload import VkUpload
import requests
import telebot
from telebot.types import Message

# ========== ДИНАМИЧЕСКАЯ ЗАГРУЗКА ГЕНЕРАТОРОВ ==========
from core.utils import load_generator
from core.base import TextGenerator, ImageGenerator

TEXT_GENERATOR_CLASS = os.getenv("TEXT_GENERATOR_CLASS", "generators.text.dummy:DummyTextGenerator")
IMAGE_GENERATOR_CLASS = os.getenv("IMAGE_GENERATOR_CLASS", "generators.image.multi:MultiImageGenerator")

text_gen = None
image_gen = None

def init_generators():
    global text_gen, image_gen
    try:
        mod, cls = TEXT_GENERATOR_CLASS.split(":")
        text_gen = load_generator(mod, cls, TextGenerator)
        if text_gen is None:
            from generators.text.dummy import DummyTextGenerator
            text_gen = DummyTextGenerator()
            logger.warning("Текст: заглушка")
    except Exception as e:
        logger.error(f"Ошибка загрузки текстового генератора: {e}")
        from generators.text.dummy import DummyTextGenerator
        text_gen = DummyTextGenerator()

    try:
        mod, cls = IMAGE_GENERATOR_CLASS.split(":")
        image_gen = load_generator(mod, cls, ImageGenerator)
        if image_gen is None:
            from generators.image.dummy import DummyImageGenerator
            image_gen = DummyImageGenerator()
            logger.warning("Изображения: заглушка")
    except Exception as e:
        logger.error(f"Ошибка загрузки генератора изображений: {e}")
        from generators.image.dummy import DummyImageGenerator
        image_gen = DummyImageGenerator()

    logger.info("Генераторы загружены")

# ========== ГРУППЫ ==========
def load_groups() -> Dict[str, Dict]:
    if GROUPS_FILE.exists():
        with open(GROUPS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_groups(groups: Dict[str, Dict]):
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)

def add_group(name: str, token: str, group_id: int) -> bool:
    groups = load_groups()
    if name in groups:
        return False
    groups[name] = {"token": token, "group_id": group_id}
    save_groups(groups)
    return True

def remove_group(name: str) -> bool:
    groups = load_groups()
    if name not in groups:
        return False
    del groups[name]
    save_groups(groups)
    return True

def get_group(name: str) -> Optional[Dict]:
    groups = load_groups()
    return groups.get(name)

def get_all_groups() -> List[str]:
    return list(load_groups().keys())

# load_default_group_from_env():
    token = os.getenv("VK_TOKEN_AI")
    group_id_str = os.getenv("GROUP_ID_AI")
    if token and group_id_str:
        try:
            group_id = int(group_id_str)
            default_name = os.getenv("RSS_DEFAULT_GROUP", "Родительский")
            if add_group(default_name, token, group_id):
                logger.info("Автоматически добавлена группа '%s' (ID: %s)", default_name, group_id)
        except ValueError:
            logger.error("GROUP_ID_AI не число: %s", group_id_str)

# ========== РАСПИСАНИЕ ==========
def load_schedule() -> List[Dict[str, Any]]:
    if SCHEDULE_FILE.exists():
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_schedule(schedule: List[Dict[str, Any]]):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(schedule, f, ensure_ascii=False, indent=2)

def check_schedule():
    schedule = load_schedule()
    now = time.time()
    new_schedule = []
    for item in schedule:
        if item.get("publish_time", 0) <= now:
            try:
                result = publish_post(item["group"], item["text"], item.get("media_url"))
                logger.info("Плановый пост: %s", result)
            except Exception as e:
                logger.error("Ошибка планового поста: %s", e)
        else:
            new_schedule.append(item)
    if len(new_schedule) != len(schedule):
        save_schedule(new_schedule)

# ========== ФУНКЦИИ ГЕНЕРАЦИИ ==========
def generate_text(topic: str) -> str:
    return text_gen.generate(topic)

def generate_image(prompt: str, **kwargs) -> Optional[str]:
    return image_gen.generate(prompt, **kwargs)

# ========== ПУБЛИКАЦИЯ ==========
def publish_post(group_name: str, text: str, image_url: Optional[str] = None) -> str:
    group_data = get_group(group_name)
    if not group_data:
        return f"❌ Группа '{group_name}' не найдена. Добавьте её через /add"
    token = group_data["token"]
    group_id = int(group_data["group_id"])

    try:
        vk = vk_api.VkApi(token=token)
        api = vk.get_api()
        upload = VkUpload(api)
    except Exception as e:
        return f"❌ Ошибка авторизации: {e}"

    attachments = []
    if image_url:
        try:
            logger.info(f"Попытка загрузить фото по URL: {image_url}")

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Referer": "https://www.google.com/"
            }
            resp = requests.get(image_url, headers=headers, timeout=30)
            resp.raise_for_status()

            content_type = resp.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                logger.warning(f"URL вернул не изображение (content-type: {content_type}), пробуем без реферера")
                resp = requests.get(image_url, timeout=30)
                resp.raise_for_status()
                content_type = resp.headers.get('content-type', '')
                if not content_type.startswith('image/'):
                    logger.warning(f"URL не ведёт на изображение, публикуем без фото")
                    return publish_post(group_name, text, None)

            img_data = resp.content
            if not img_data or len(img_data) < 1000:
                raise ValueError("Получены пустые данные изображения")

            magic = img_data[:4]
            if not (magic.startswith(b'\xff\xd8\xff') or magic.startswith(b'\x89PNG') or
                    magic.startswith(b'GIF8') or magic.startswith(b'RIFF')):
                logger.warning("Файл не похож на изображение, пропускаем картинку")
                return publish_post(group_name, text, None)

            temp_path = DATA_DIR / f"temp_{random.randint(1, 1000000)}.jpg"
            with open(temp_path, "wb") as f:
                f.write(img_data)

            photo = upload.photo_wall(str(temp_path), group_id=abs(group_id))
            os.remove(temp_path)

            attachments.append(f"photo{photo[0]['owner_id']}_{photo[0]['id']}")
            logger.info("Фото успешно загружено на стену")

        except Exception as e:
            logger.error(f"Ошибка загрузки фото: {e}")
            return publish_post(group_name, text, None)

    try:
        params = {
            "owner_id": group_id,
            "message": text,
            "access_token": token,
            "v": "5.131",
            "from_group": 1,
        }
        if attachments:
            params["attachments"] = ",".join(attachments)
        resp = api.wall.post(**params)
        post_id = resp.get("post_id")
        logger.info("Пост опубликован в '%s', id=%s", group_name, post_id)
        return f"✅ Пост опубликован в '{group_name}' (id: {post_id})"
    except Exception as e:
        logger.error("Ошибка публикации: %s", e)
        return f"❌ Ошибка публикации: {e}"

# ========== ПАРСИНГ КОМАНД ==========
def parse_command(text: str) -> Optional[Dict[str, Any]]:
    text = text.replace("&quot;", '"').replace("&amp;", "&")
    pattern = r'пост в\s*"([^"]+)"\s*на тему\s*"([^"]+)"\s*(?:с\s*(фото|видео)\s*(https?://\S+))?\s*(?:через\s*(\d+)\s*минут)?'
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None
    group = match.group(1).strip()
    topic = match.group(2).strip()
    media_type = match.group(3)
    media_url = match.group(4) if media_type else None
    delay = int(match.group(5)) if match.group(5) else 0
    return {"group": group, "topic": topic, "media_url": media_url, "delay": delay, "media_type": media_type}

def handle_command(cmd: str) -> str:
    parsed = parse_command(cmd)
    if not parsed:
        return "❌ Неверный формат. Используйте: пост в \"Группа\" на тему \"Тема\" [с фото ссылка] [через X минут]"

    group = parsed["group"]
    topic = parsed["topic"]
    media_url = parsed["media_url"]
    delay = parsed["delay"]

    text = generate_text(topic)
    image_url = media_url
    if not image_url:
        try:
            prompt = f"Иллюстрация к посту на тему: {topic}"
            image_url = generate_image(prompt)
        except Exception as e:
            logger.error("Ошибка генерации картинки: %s", e)
            image_url = None

    if delay > 0:
        schedule = load_schedule()
        schedule.append({
            "group": group,
            "text": text,
            "media_url": image_url,
            "publish_time": int(time.time()) + delay * 60
        })
        save_schedule(schedule)
        return f"⏳ Пост для '{group}' запланирован через {delay} мин"
    else:
        return publish_post(group, text, image_url)

# ========== ДЛЯ RSS ==========
def handle_publication(group_name: str, topic: str) -> str:
    text = generate_text(topic)
    prompt = f"Иллюстрация к посту на тему: {topic}"
    image_url = generate_image(prompt)
    return publish_post(group_name, text, image_url)

# ========== TELEGRAM ==========
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "👋 Привет! Я бот-менеджер для публикации постов в ВК.\n\n"
        "📌 Команды:\n"
        "/add \"Название\" ТОКЕН ID_ГРУППЫ – добавить группу\n"
        "/list – показать все группы\n"
        "/remove \"Название\" – удалить группу\n"
        "✍️ Для публикации отправьте:\n"
        "пост в \"Группа\" на тему \"Текст\" [с фото ссылка] [через X минут]"
    )

@bot.message_handler(commands=['add'])
def add_group_command(message):
    pattern = r'/add\s+"([^"]+)"\s+(\S+)\s+(-?\d+)'
    match = re.search(pattern, message.text)
    if not match:
        bot.reply_to(message, "❌ Используйте: /add \"Название группы\" ТОКЕН ID_ГРУППЫ")
        return
    name = match.group(1)
    token = match.group(2)
    try:
        group_id = int(match.group(3))
    except ValueError:
        bot.reply_to(message, "❌ ID должен быть числом (с минусом, если группа отрицательная)")
        return
    if add_group(name, token, group_id):
        bot.reply_to(message, f"✅ Группа '{name}' добавлена (ID: {group_id})")
    else:
        bot.reply_to(message, f"❌ Группа '{name}' уже существует")

@bot.message_handler(commands=['list'])
def list_groups_command(message):
    groups = get_all_groups()
    if not groups:
        bot.reply_to(message, "📭 Нет групп")
    else:
        bot.reply_to(message, "📋 Группы:\n" + "\n".join(f"• {g}" for g in groups))

@bot.message_handler(commands=['remove'])
def remove_group_command(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "❌ Используйте: /remove \"Название\"")
        return
    name = args[1].strip('"')
    if remove_group(name):
        bot.reply_to(message, f"✅ Группа '{name}' удалена")
    else:
        bot.reply_to(message, f"❌ Группа '{name}' не найдена")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text and not message.text.startswith('/'):
        response = handle_command(message.text)
        bot.reply_to(message, response)

# ========== HEALTH ==========
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ['/', '/health']:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)

def run_health_server():
    server = HTTPServer(('0.0.0.0', HEALTH_PORT), HealthHandler)
    logger.info("Health-сервер на порту %s", HEALTH_PORT)
    server.serve_forever()

# ========== RSS-ПЛАНИРОВЩИК ==========
def run_rss_scheduler(publish_func):
    try:
        import feedparser
    except ImportError:
        logger.error("feedparser не установлен, RSS-планировщик отключён")
        return
    from datetime import datetime
    POST_TIMES = [(10,0), (14,0), (16,0), (21,0)]
    STATE_FILE = DATA_DIR / "rss_state.json"
    def load_state():
        if STATE_FILE.exists():
            with open(STATE_FILE, "r") as f:
                try:
                    return json.load(f)
                except:
                    return {}
        return {}
    def save_state(state):
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    def parse_rss_feed(url):
        try:
            feed = feedparser.parse(url)
            entries = []
            for entry in feed.entries:
                title = entry.get("title", "").strip()
                if title:
                    entries.append(title)
            return entries
        except Exception as e:
            logger.error(f"Ошибка парсинга RSS {url}: {e}")
            return []
    def get_all_topics():
        all_topics = []
        for source in RSS_SOURCES:
            url = source.get("url")
            if url:
                topics = parse_rss_feed(url)
                all_topics.extend(topics)
        return all_topics
    def select_topics(all_topics, limit=4):
        random.shuffle(all_topics)
        return all_topics[:limit]
    def get_topics_for_today():
        state = load_state()
        today = datetime.now().strftime("%Y-%m-%d")
        if state.get("date") == today and "topics" in state:
            return state["topics"]
        all_topics = get_all_topics()
        if not all_topics:
            logger.warning("Нет записей из RSS-источников")
            return ["Новости для родителей"] * 4
        topics = select_topics(all_topics, 4)
        state["date"] = today
        state["topics"] = topics
        save_state(state)
        return topics
    def should_publish_now(target_hour, target_minute):
        now = datetime.now()
        return (now.hour == target_hour and now.minute == target_minute and now.second < 5)
    published_today = {}
    logger.info("RSS-планировщик запущен")
    while True:
        try:
            now = datetime.now()
            today = now.strftime("%Y-%m-%d")
            for hour, minute in POST_TIMES:
                if should_publish_now(hour, minute):
                    key = f"{today}_{hour}_{minute}"
                    if key in published_today:
                        continue
                    topics = get_topics_for_today()
                    if topics:
                        topic = topics.pop(0)
                        state = load_state()
                        state["topics"] = topics
                        save_state(state)
                        logger.info(f"Автоматическая публикация в {hour:02d}:{minute:02d}: {topic}")
                        result = publish_func("Родительский", topic)
                        logger.info(f"Результат публикации: {result}")
                        published_today[key] = True
                    else:
                        logger.warning("Нет доступных тем")
            if today not in str(published_today):
                published_today = {}
        except Exception as e:
            logger.error(f"Ошибка в RSS-планировщике: {e}")
        time.sleep(30)

# ========== MAIN ==========
def main():
    logger.info("🚀 БОТ ЗАПУЩЕН")
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN не задан")
        sys.exit(1)

    init_generators()
    load_default_group_from_env()

    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    def schedule_loop():
        while True:
            try:
                check_schedule()
            except Exception as e:
                logger.error("Ошибка планировщика: %s", e)
            time.sleep(30)
    schedule_thread = threading.Thread(target=schedule_loop, daemon=True)
    schedule_thread.start()

    try:
        rss_thread = threading.Thread(target=run_rss_scheduler, args=(handle_publication,), daemon=True)
        rss_thread.start()
    except Exception as e:
        logger.error(f"Ошибка запуска RSS-планировщика: {e}")

    try:
        logger.info("Telegram бот запущен")
        bot.infinity_polling(timeout=10, long_polling_timeout=10)
    except Exception as e:
        logger.error("Ошибка polling: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
