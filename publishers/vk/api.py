"""
publishers/vk/api.py
---------------------------------------
Базовый клиент VK API.
"""

from __future__ import annotations

from typing import Any

from core.http import http
from core.logger import get_logger


class VKApi:
    """
    Универсальный клиент VK API.
    """

    API_VERSION = "5.199"

    BASE_URL = "https://api.vk.com/method"

    def __init__(self, token: str):

        self.token = token

        self.logger = get_logger(self.__class__.__name__)

    # ==================================================

    def method(
        self,
        method: str,
        **params,
    ) -> dict[str, Any]:

        params["access_token"] = self.token
        params["v"] = self.API_VERSION

        url = f"{self.BASE_URL}/{method}"

        self.logger.debug("VK -> %s", method)

        data = http.post_json(

            url,

            data=params,

        )

        if "error" in data:

            error = data["error"]

            raise RuntimeError(

                f"VK [{error['error_code']}] "
                f"{error['error_msg']}"

            )

        return data["response"]

    # ==================================================

    def get(
        self,
        method: str,
        **params,
    ):

        return self.method(

            method,

            **params,

        )

    # ==================================================

    def post(
        self,
        method: str,
        **params,
    ):

        return self.method(

            method,

            **params,

        )