"""
Главная точка входа проекта.
"""

from core.logger import get_logger
from core.groups import groups

from generators.text.manager import text_manager
from generators.image.multi import multi_image

from publishers.vk.publisher import VKPublisher


logger = get_logger("BOT")


def main():

    logger.info("Запуск проекта...")

    # ----------------------------------------
    # Выбираем группу
    # ----------------------------------------

    group = groups.first()

    if group is None:

        logger.error("Нет доступных групп.")

        return

    logger.info(
        "Выбрана группа: %s",
        group.name,
    )

    # ----------------------------------------
    # Тема
    # ----------------------------------------

    topic = input(
        "\nВведите тему публикации: "
    ).strip()

    if not topic:

        logger.error("Тема не указана.")

        return

    # ----------------------------------------
    # Генерация текста
    # ----------------------------------------

    logger.info("Генерация текста...")

    post = text_manager.generate(topic)

    # ----------------------------------------
    # Генерация изображения
    # ----------------------------------------

    logger.info("Генерация изображения...")

    image = multi_image.generate(topic)

    post.add_image(str(image))

    # ----------------------------------------
    # Публикация
    # ----------------------------------------

    logger.info("Публикация...")

    publisher = VKPublisher(group.token)

    result = publisher.publish(
        post,
        group,
    )

    # ----------------------------------------
    # Результат
    # ----------------------------------------

    if result.ok:

        logger.info(
            "Пост опубликован."
        )

        logger.info(
            "ID поста: %s",
            result.post_id,
        )

    else:

        logger.error(
            result.message
        )


if __name__ == "__main__":

    main()