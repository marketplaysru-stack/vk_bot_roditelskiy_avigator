"""publishers/uploader/imgbb.py"""
import requests
import base64
import logging
from models.upload_result import UploadResult
from config import config

logger = logging.getLogger("imgbb")

class ImgbbUploader:
    def __init__(self):
        self.api_key = config.imgbb_api_key
        if not self.api_key:
            logger.warning("IMGBB_API_KEY не задан")

    def upload(self, image_bytes: bytes) -> UploadResult:
        if not self.api_key:
            return UploadResult(success=False, error="IMGBB_API_KEY не задан")

        url = "https://api.imgbb.com/1/upload"
        b64 = base64.b64encode(image_bytes).decode('utf-8')
        payload = {"key": self.api_key, "image": b64}

        try:
            logger.info(f"Отправка запроса на imgbb, размер данных: {len(b64)} символов")
            resp = requests.post(url, data=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if data.get("success"):
                image_url = data["data"]["url"]
                logger.info(f"imgbb успешно вернул URL: {image_url}")
                return UploadResult(success=True, url=image_url)
            else:
                logger.error(f"imgbb ошибка: {data}")
                return UploadResult(success=False, error=str(data))
        except Exception as e:
            logger.error(f"Ошибка загрузки на imgbb: {e}")
            return UploadResult(success=False, error=str(e))