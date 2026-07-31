from __future__ import annotations
from typing import Optional
from models.group import Group
from config import config

class GroupsManager:
    def __init__(self):
        self._groups = self._load_groups()

    def _load_groups(self):
        groups = {}
        for name, cfg in config.groups.items():
            groups[name] = Group(
                name=name,
                group_id=cfg.group_id,
                token=cfg.vk_token,
                enabled=cfg.enabled,
                category=cfg.category,
                style=cfg.style,
            )
        return groups

    def first(self) -> Optional[Group]:
        for g in self._groups.values():
            if g.enabled:
                return g
        return None

    def get(self, name: str) -> Optional[Group]:
        return self._groups.get(name)

    def all(self):
        return list(self._groups.values())

groups = GroupsManager()