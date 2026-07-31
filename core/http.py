"""
core/http.py
---------------------------------------
Единый HTTP-клиент проекта.
"""

from __future__ import annotations

from typing import Any

import requests

from core.logger import get_logger


class HttpClient:

    DEFAULT_TIMEOUT = 60

    def __init__(self):

        self.logger = get_logger(self.__class__.__name__)

        self.session = requests.Session()

    # ==================================================

    def get(
        self,
        url: str,
        **kwargs,
    ) -> requests.Response:

        timeout = kwargs.pop(
            "timeout",
            self.DEFAULT_TIMEOUT,
        )

        self.logger.debug("GET %s", url)

        response = self.session.get(

            url,

            timeout=timeout,

            **kwargs,

        )

        response.raise_for_status()

        return response

    # ==================================================

    def post(
        self,
        url: str,
        **kwargs,
    ) -> requests.Response:

        timeout = kwargs.pop(

            "timeout",

            self.DEFAULT_TIMEOUT,

        )

        self.logger.debug("POST %s", url)

        response = self.session.post(

            url,

            timeout=timeout,

            **kwargs,

        )

        response.raise_for_status()

        return response

    # ==================================================

    def download(
        self,
        url: str,
        path: str,
        **kwargs,
    ):

        response = self.get(

            url,

            stream=True,

            **kwargs,

        )

        with open(path, "wb") as f:

            for chunk in response.iter_content(
                8192
            ):

                if chunk:

                    f.write(chunk)

        return path


http = HttpClient()