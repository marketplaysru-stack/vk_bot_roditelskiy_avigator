"""
publishers/vk/photos.py
---------------------------------------
Работа с фотографиями VK.
"""

from __future__ import annotations

from pathlib import Path

from core.http import http
from core.logger import get_logger

from publishers.vk.api import VKApi


class VKPhotos:

    def __init__(self, api: VKApi):

        self.api = api

        self.logger = get_logger(self.__class__.__name__)

    # ==================================================

    def get_upload_server(
        self,
        group_id: int,
    ) -> str:

        response = self.api.method(

            "photos.getWallUploadServer",

            group_id=abs(group_id),

        )

        return response["upload_url"]

    # ==================================================

    def upload(
        self,
        upload_url: str,
        image: str | Path,
    ) -> dict:

        path = Path(image)

        with path.open("rb") as file:

            response = http.post_json(

                upload_url,

                files={

                    "photo": file,

                },

            )

        return response

    # ==================================================

    def save(
        self,
        group_id: int,
        upload_result: dict,
    ) -> str:

        response = self.api.method(

            "photos.saveWallPhoto",

            group_id=abs(group_id),

            photo=upload_result["photo"],

            server=upload_result["server"],

            hash=upload_result["hash"],

        )

        photo = response[0]

        return f'photo{photo["owner_id"]}_{photo["id"]}'

    # ==================================================

    def upload_photo(
        self,
        group_id: int,
        image: str | Path,
    ) -> str:
        """
        Полный цикл загрузки изображения.
        """

        upload_url = self.get_upload_server(
            group_id
        )

        upload_result = self.upload(
            upload_url,
            image,
        )

        return self.save(
            group_id,
            upload_result,
        )