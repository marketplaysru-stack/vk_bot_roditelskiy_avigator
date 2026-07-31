"""
scheduler.py
---------------------------------------
Планировщик задач проекта.

Отвечает только за запуск задач по времени.
Не содержит логики публикации.
"""

from __future__ import annotations

import logging
from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from config import config

logger = logging.getLogger("scheduler")


class Scheduler:

    def __init__(self):

        self.scheduler = BackgroundScheduler(
            timezone=config.timezone
        )

        self.started = False

    # -------------------------------------------------

    def start(self):

        if self.started:
            return

        self.scheduler.start()

        self.started = True

        logger.info("Планировщик запущен")

    # -------------------------------------------------

    def stop(self):

        if not self.started:
            return

        self.scheduler.shutdown(wait=False)

        self.started = False

        logger.info("Планировщик остановлен")

    # -------------------------------------------------

    def add_daily_job(
        self,
        func: Callable,
        hour: int,
        minute: int = 0,
        job_id: str | None = None
    ):

        self.scheduler.add_job(
            func,
            trigger=CronTrigger(
                hour=hour,
                minute=minute
            ),
            id=job_id,
            replace_existing=True
        )

        logger.info(
            "Добавлена задача %s (%02d:%02d)",
            job_id,
            hour,
            minute
        )

    # -------------------------------------------------

    def add_interval_job(
        self,
        func: Callable,
        minutes: int,
        job_id: str | None = None
    ):

        self.scheduler.add_job(
            func,
            trigger="interval",
            minutes=minutes,
            id=job_id,
            replace_existing=True
        )

        logger.info(
            "Добавлена интервальная задача %s (%d мин)",
            job_id,
            minutes
        )

    # -------------------------------------------------

    def remove_job(self, job_id: str):

        try:

            self.scheduler.remove_job(job_id)

            logger.info(
                "Удалена задача %s",
                job_id
            )

        except Exception:

            logger.warning(
                "Задача %s не найдена",
                job_id
            )

    # -------------------------------------------------

    def list_jobs(self):

        return self.scheduler.get_jobs()

    # -------------------------------------------------

    def schedule_post_times(
        self,
        func: Callable
    ):

        """
        Создает задачи по времени,
        указанному в config.post_times
        """

        for index, post_time in enumerate(config.post_times):

            hour, minute = map(
                int,
                post_time.split(":")
            )

            self.add_daily_job(
                func=func,
                hour=hour,
                minute=minute,
                job_id=f"publish_{index}"
            )

        logger.info(
            "Создано %d задач публикации",
            len(config.post_times)
        )


# -------------------------------------------------

scheduler = Scheduler()