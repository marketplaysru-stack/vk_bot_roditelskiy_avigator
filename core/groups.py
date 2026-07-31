def load(self):

    self.groups.clear()

    if not self.filename.exists():

        self.logger.warning(
            "Файл групп не найден: %s",
            self.filename,
        )

        return

    with self.filename.open(
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    for item in data:

        token_name = item.get("token", "")

        if token_name:

            token = getattr(settings, token_name, "")

            item["token"] = token

        self.groups.append(
            Group.from_dict(item)
        )

    self.logger.info(
        "Загружено групп: %s",
        len(self.groups),
    )