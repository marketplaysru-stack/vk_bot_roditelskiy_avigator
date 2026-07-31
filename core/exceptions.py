"""
core/exceptions.py
---------------------------------------
Общие исключения проекта.

Все пользовательские ошибки наследуются
от ProjectError.
"""


class ProjectError(Exception):
    """Базовое исключение проекта."""
    pass


# ==================================================
# CONFIG
# ==================================================

class ConfigError(ProjectError):
    """Ошибка конфигурации."""
    pass


# ==================================================
# TELEGRAM
# ==================================================

class TelegramError(ProjectError):
    """Ошибка Telegram API."""
    pass


# ==================================================
# VK
# ==================================================

class VKError(ProjectError):
    """Ошибка VK API."""
    pass


class VKUploadError(VKError):
    """Ошибка загрузки изображения."""
    pass


class VKPublishError(VKError):
    """Ошибка публикации поста."""
    pass


# ==================================================
# AI
# ==================================================

class GeneratorError(ProjectError):
    """Общая ошибка генератора."""
    pass


class TextGeneratorError(GeneratorError):
    """Ошибка генерации текста."""
    pass


class ImageGeneratorError(GeneratorError):
    """Ошибка генерации изображения."""
    pass


# ==================================================
# RSS
# ==================================================

class RSSError(ProjectError):
    """Ошибка RSS."""
    pass


# ==================================================
# DATABASE
# ==================================================

class DatabaseError(ProjectError):
    """Ошибка базы данных."""
    pass


# ==================================================
# NETWORK
# ==================================================

class NetworkError(ProjectError):
    """Ошибка сети."""
    pass


class TimeoutError(NetworkError):
    """Превышено время ожидания."""
    pass


# ==================================================
# FILES
# ==================================================

class FileError(ProjectError):
    """Ошибка файла."""
    pass


class ImageError(FileError):
    """Ошибка изображения."""
    pass


class JsonError(FileError):
    """Ошибка JSON."""
    pass


# ==================================================
# SCHEDULER
# ==================================================

class SchedulerError(ProjectError):
    """Ошибка планировщика."""
    pass


# ==================================================
# HEALTH
# ==================================================

class HealthCheckError(ProjectError):
    """Ошибка проверки сервисов."""
    pass