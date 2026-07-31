"""
publishers/uploader/imgbb.py
---------------------------------------
Загрузка изображений в ImgBB.
"""

from __future__ import annotations

import base64
from pathlib import Path

import requests

from config import settings

from models.upload_result import UploadResult

from publishers.uploader.base import BaseUploader


class ImgbbUploader(BaseUploader):

    name = "imgbb"

    API_URL = "https://api.imgbb.com/1/upload"

    # ==========================================

    def upload(
        self,
        image,
        **kwargs,
    ) -> UploadResult:

        try:

            path = self.validate(image)

            self.before_upload(path)

            with open(path, "rb") as f:

                encoded = base64.b64encode(
                    f.read()
                ).decode()

            response = requests.post(

                self.API_URL,

                timeout=60,

                data={

                    "key": settings.IMGBB_API_KEY,

                    "image": encoded,

                }

            )

            response.raise_for_status()

            data = response.json()

            if not data.get("success"):

                return UploadResult.error_result(

                    provider=self.name,

                    message="ImgBB вернул ошибку."

                )

            image_data = data["data"]

            result = UploadResult.success_result(

                provider=self.name,

                url=image_data["url"],

                upload_id=image_data["id"],

                file_name=path.name,

                file_path=str(path),

                size=path.stat().st_size,

                width=int(image_data["width"]),

                height=int(image_data["height"]),

                metadata=image_data,

            )

            return self.after_upload(result)

        except Exception as exc:

            return UploadResult.error_result(

                provider=self.name,

                message=str(exc),

                exception=repr(exc),

            )