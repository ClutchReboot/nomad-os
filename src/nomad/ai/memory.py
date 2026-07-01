"""Simple memory placeholder."""


class Memory:
    """Store and retrieve robot memories."""

    def __init__(self) -> None:
        self._items: list[str] = []

    def add(self, item: str) -> None:
        self._items.append(item)

    def all(self) -> list[str]:
        return list(self._items)
