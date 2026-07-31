"""
core/health.py
----------------------------------------
Мониторинг состояния сервисов проекта.
"""

from __future__ import annotations

import socket
from dataclasses import dataclass
from typing import Callable

import requests

from config import config
from core.logger import get_logger

logger = get_logger(__name__)


# =====================================================
# RESULT
# =====================================================

@dataclass(slots=True)
class HealthResult:

    name: str

    ok: bool

    message: str = ""


# =====================================================
# HEALTH
# =====================================================

class HealthCheck:

    def __init__(self):

        self.checks: list[tuple[str, Callable]] = []

    # -------------------------------------------------

    def register(
        self,
        name: str,
        func: Callable
    ):

        self.checks.append(
            (
                name,
                func
            )
        )

    # -------------------------------------------------

    def run(self):

        results = []

        for name, func in self.checks:

            try:

                ok = func()

                results.append(

                    HealthResult(

                        name=name,

                        ok=bool(ok),

                        message="OK" if ok else "FAILED"

                    )

                )

            except Exception as e:

                logger.exception(e)

                results.append(

                    HealthResult(

                        name=name,

                        ok=False,

                        message=str(e)

                    )

                )

        return results

    # -------------------------------------------------

    def print(self):

        for item in self.run():

            status = "✅" if item.ok else "❌"

            logger.info(
                "%s %s (%s)",
                status,
                item.name,
                item.message
            )


health = HealthCheck()


# =====================================================
# CHECKS
# =====================================================

def check_internet():

    socket.create_connection(

        ("8.8.8.8", 53),

        timeout=3

    )

    return True


def check_vk():

    requests.get(

        "https://api.vk.com",

        timeout=10

    )

    return True


def check_pollinations():

    requests.get(

        config.pollinations_url,

        timeout=20

    )

    return True


def check_imgbb():

    requests.get(

        "https://api.imgbb.com",

        timeout=10

    )

    return True


def check_telegram():

    requests.get(

        f"https://api.telegram.org/bot{config.telegram_token}/getMe",

        timeout=10

    )

    return True


# =====================================================
# РЕГИСТРАЦИЯ
# =====================================================

health.register(
    "Internet",
    check_internet
)

health.register(
    "Telegram",
    check_telegram
)

health.register(
    "VK",
    check_vk
)

health.register(
    "Pollinations",
    check_pollinations
)

health.register(
    "ImgBB",
    check_imgbb
)