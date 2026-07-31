"""publishers/vk/publisher.py"""
import vk_api
from vk_api.upload import VkUpload
import requests
import random
import os
from pathlib import Path

from core.logger import get_logger
from models.group import Group
from models.post import Post
from models.publish_result import PublishResult

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
                # Загружаем байты напрямую в VK
                cache_dir = Path("cache/images")
                cache_dir.mkdir(parents=True, exist_ok=True)
                temp_path = cache_dir / f"temp_{random.randint(1, 1000000)}.jpg"
                temp_path.write_bytes(post.image_bytes)
                photo = upload.photo_wall(str(temp_path), group_id=abs(group.vk_owner_id))
                os.remove(temp_path)
                attachments.append(f"photo{photo[0]['owner_id']}_{photo[0]['id']}")
            elif post.image_url:
                # Если вдруг есть URL (для совместимости)
                img_resp = requests.get(post.image_url, timeout=30)
                img_resp.raise_for_status()
                cache_dir = Path("cache/images")
                cache_dir.mkdir(parents=True, exist_ok=True)
                temp_path = cache_dir / f"temp_{random.randint(1, 1000000)}.jpg"
                temp_path.write_bytes(img_resp.content)
                photo = upload.photo_wall(str(temp_path), group_id=abs(group.vk_owner_id))
                os.remove(temp_path)
                attachments.append(f"photo{photo[0]['owner_id']}_{photo[0]['id']}")

            params = {
                "owner_id": group.vk_owner_id,
                "message": post.text,
                "access_token": self.token,
                "v": "5.131"
            }
            if group.group_id < 0:
                params["from_group"] = 1
            if attachments:
                params["attachments"] = ",".join(attachments)

            resp = api.wall.post(**params)
            return PublishResult(ok=True, post_id=resp.get("post_id"))

        except Exception as e:
            logger.error(f"Ошибка публикации: {e}")
            return PublishResult(ok=False, message=str(e))