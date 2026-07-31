"""publishers/vk/publisher.py"""
import vk_api
from vk_api.upload import VkUpload
import random
import os
from pathlib import Path
from typing import Optional

from core.logger import get_logger
from models.group import Group
from models.post import Post
from models.publish_result import PublishResult
from config import config

logger = get_logger("VKPublisher")

class VKPublisher:
    def __init__(self, token: str):
        self.token = token

    def publish(self, post: Post, group: Group) -> PublishResult:
        try:
            vk = vk_api.VkApi(token=self.token)
            api = vk.get_api()
            upload = VkUpload(api)

            attachments = []
            if post.image_bytes:
                cache_dir = Path("cache/images")
                cache_dir.mkdir(parents=True, exist_ok=True)
                temp_path = cache_dir / f"temp_{random.randint(1, 1000000)}.jpg"
                temp_path.write_bytes(post.image_bytes)
                photo = upload.photo_wall(str(temp_path), group_id=abs(group.vk_owner_id))
                os.remove(temp_path)
                attachments.append(f"photo{photo[0]['owner_id']}_{photo[0]['id']}")

            params = {
                "owner_id": group.vk_owner_id,
                "message": post.text,
                "access_token": self.token,
                "v": "5.131"
            }
            if attachments:
                params["attachments"] = ",".join(attachments)

            resp = api.wall.post(**params)
            return PublishResult(ok=True, post_id=resp.get("post_id"))

        except Exception as e:
            logger.error(f"Ошибка публикации: {e}")
            return PublishResult(ok=False, message=str(e))

    # ----- НОВЫЙ МЕТОД ДЛЯ ЛИЧНОЙ СТРАНИЦЫ -----
    def publish_to_user(self, text: str, image_bytes: Optional[bytes] = None, link: Optional[str] = None) -> PublishResult:
        """Публикует анонс на личную стену пользователя."""
        try:
            vk = vk_api.VkApi(token=self.token)
            api = vk.get_api()
            upload = VkUpload(api)

            attachments = []
            if image_bytes:
                cache_dir = Path("cache/images")
                cache_dir.mkdir(parents=True, exist_ok=True)
                temp_path = cache_dir / f"temp_user_{random.randint(1, 1000000)}.jpg"
                temp_path.write_bytes(image_bytes)
                photo = upload.photo_wall(str(temp_path))
                os.remove(temp_path)
                attachments.append(f"photo{photo[0]['owner_id']}_{photo[0]['id']}")

            full_text = text
            if link:
                full_text += f"\n\n👉 {link}"

            params = {
                "owner_id": config.vk_user_id,
                "message": full_text,
                "access_token": self.token,
                "v": "5.131"
            }
            if attachments:
                params["attachments"] = ",".join(attachments)

            resp = api.wall.post(**params)
            return PublishResult(ok=True, post_id=resp.get("post_id"))

        except Exception as e:
            logger.error(f"Ошибка публикации на личную стену: {e}")
            return PublishResult(ok=False, message=str(e))