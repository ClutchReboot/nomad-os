"""Simple in-process publish/subscribe event bus."""

from collections import defaultdict
from collections.abc import Callable
import logging
from typing import Any


EventHandler = Callable[[dict[str, Any]], None]


class EventBus:
    """Route named events between robot modules."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._logger = logger or logging.getLogger(__name__)

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self._handlers[event_name].append(handler)

    def publish(self, event_name: str, payload: dict[str, Any] | None = None) -> None:
        for handler in self._handlers[event_name]:
            try:
                handler(payload or {})
            except Exception:
                self._logger.exception("Event handler failed for %s", event_name)
