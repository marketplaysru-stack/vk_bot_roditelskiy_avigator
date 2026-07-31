"""publishers/vk/publisher.py"""
import vk_api
from vk_api.upload import VkUpload
import random
import os
from pathlib import Path
from typing import Optional
from PIL import Image
import io

from core.logger import get_logger
from models.group import Group
from models.post import Post
from models.publish_result import PublishResult
from config import config

logger = get_logger("VKPublisher")

class VKPublisher:
    def __init__(self, token: str):
        self.token = token

    def _prepare_image(self, image_bytes: bytes) -> Optional[bytes]:
        """Проверяет и конвертирует изображение в JPEG, если необходимо."""
        try:
            # Пытаемся открыть изображение
            img = Image.open(io.BytesIO(image_bytes))
            # Конвертируем в RGB (если RGBA) и сохраняем как JPEG
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            # Сохраняем в буфер
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=90)
            return buf.getvalue()
        except Exception as e:
            logger.error(f"Ошибка подготовки изображения: {e}")
            return None

    def publish(self, post: Post, group: Group) -> PublishResult:
        try:
            vk = vk_api.VkApi(token=self.token)
            api = vk.get_api()
            upload = VkUpload(api)

            attachments = []
            if post.image_bytes:
                # Подготавливаем изображение
                prepared = self._prepare_image(post.image_bytes)
                if not prepared:
                    logger.error("Не удалось подготовить изображение, публикуем без фото")
                    return self._publish_text_only(api, group, post.text)

                # Сохраняем временный файл
                cache_dir = Path("cache/images")
                cache_dir.mkdir(parents=True, exist_ok=True)
                temp_path = cache_dir / f"temp_{random.randint(1, 1000000)}.jpg"
                temp_path.write_bytes(prepared)
                logger.info(f"Временный файл сохранён: {temp_path}")

                try:
                    photo = upload.photo_wall(str(temp_path), group_id=abs(group.vk_owner_id))
                    if photo and isinstance(photo, list) and len(photo) > 0:
                        attachments.append(f"photo{photo[0]['owner_id']}_{photo[0]['id']}")
                        logger.info("Фото успешно загружено в группу")
                    else:
                        logger.warning("Загрузка фото вернула пустой результат")
                except Exception as e:
                    logger.error(f"Ошибка загрузки фото: {e}")
                finally:
                    if temp_path.exists():
                        try:
                            os.remove(temp_path)
                        except:
                            pass

            # Публикация
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
            logger.error(f"Ошибка публикации в группу: {e}")
            return PublishResult(ok=False, message=str(e))

    def publish_to_user(self, text: str, image_bytes: Optional[bytes] = None, link: Optional[str] = None) -> PublishResult:
        """Публикует анонс на личную стену пользователя."""
        try:
            vk = vk_api.VkApi(token=self.token)
            api = vk.get_api()
            upload = VkUpload(api)

            attachments = []
            if image_bytes:
                prepared = self._prepare_image(image_bytes)
                if prepared:
                    cache_dir = Path("cache/images")
                    cache_dir.mkdir(parents=True, exist_ok=True)
                    temp_path = cache_dir / f"temp_user_{random.randint(1, 1000000)}.jpg"
                    temp_path.write_bytes(prepared)
                    try:
                        photo = upload.photo_wall(str(temp_path))
                        if photo and isinstance(photo, list) and len(photo) > 0:
                            attachments.append(f"photo{photo[0]['owner_id']}_{photo[0]['id']}")
                            logger.info("Фото для анонса загружено")
                    except Exception as e:
                        logger.error(f"Ошибка загрузки фото для анонса: {e}")
                    finally:
                        if temp_path.exists():
                            try:
                                os.remove(temp_path)
                            except:
                                pass

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

    def _publish_text_only(self, api, group, text):
        """Публикует только текст (без фото)."""
        try:
            params = {
                "owner_id": group.vk_owner_id,
                "message": text,
                "access_token": self.token,
                "v": "5.131"
            }
            resp = api.wall.post(**params)
            return PublishResult(ok=True, post_id=resp.get("post_id"))
        except Exception as e:
            return PublishResult(ok=False, message=str(e))