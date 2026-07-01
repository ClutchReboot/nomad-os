"""Shared robot state."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class RobotState:
    """Current high-level state for Nomad."""

    mode: str = "idle"
    running: bool = False
    started_at: datetime | None = None
    last_heartbeat_at: datetime | None = None
    battery_percent: float | None = None
    location: dict[str, float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def mark_started(self) -> None:
        self.running = True
        self.started_at = datetime.now(timezone.utc)

    def mark_stopped(self) -> None:
        self.running = False

    def heartbeat(self) -> None:
        self.last_heartbeat_at = datetime.now(timezone.utc)

    def set_mode(self, mode: str) -> None:
        self.mode = mode
