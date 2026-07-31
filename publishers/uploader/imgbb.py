"""publishers/uploader/imgbb.py"""
import requests
import base64
from config import config
from models.upload_result import UploadResult

class ImgbbUploader:
    def __init__(self):
        self.api_key = config.imgbb_api_key

    def upload(self, image_bytes: bytes) -> UploadResult:
        if not self.api_key:
            return UploadResult(success=False, error="IMGBB_API_KEY не задан")

        url = "https://api.imgbb.com/1/upload"
        b64 = base64.b64encode(image_bytes).decode('utf-8')
        payload = {"key": self.api_key, "image": b64}

        try:
            resp = requests.post(url, data=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if data.get("success"):
                return UploadResult(success=True, url=data["data"]["url"])
            else:
                return UploadResult(success=False, error=str(data))
        except Exception as e:
            return UploadResult(success=False, error=str(e))