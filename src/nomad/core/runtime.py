"""Nomad runtime loop."""

from time import sleep
from typing import Any

from nomad.core.config import AppConfig, load_config
from nomad.core.event_bus import EventBus
from nomad.core.logger import configure_logging, get_logger
from nomad.core.state import RobotState


class RobotRuntime:
    """Coordinate core robot services and lifecycle events."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or load_config()
        configure_logging(self.config.settings.get("logging", {}).get("level", "INFO"))

        self.logger = get_logger(__name__)
        self.state = RobotState(mode=self.config.initial_mode)
        self.state.metadata["robot_name"] = self.config.robot_name
        self.event_bus = EventBus(self.logger)

        self._register_core_handlers()

    def run(self) -> None:
        """Run until interrupted."""
        self.start()

        try:
            while self.state.running:
                self.tick()
                sleep(self.config.heartbeat_seconds)
        except KeyboardInterrupt:
            self.logger.info("Shutdown requested")
        finally:
            self.stop()

    def start(self) -> None:
        self.state.mark_started()
        self.event_bus.publish(
            "system.start",
            {
                "robot_name": self.config.robot_name,
                "mode": self.state.mode,
                "root_dir": str(self.config.root_dir),
            },
        )

    def tick(self) -> None:
        self.state.heartbeat()
        self.event_bus.publish(
            "system.heartbeat",
            {
                "mode": self.state.mode,
                "battery_percent": self.state.battery_percent,
                "last_heartbeat_at": self.state.last_heartbeat_at,
            },
        )

    def stop(self) -> None:
        if not self.state.running:
            return

        self.state.mark_stopped()
        self.event_bus.publish("system.shutdown", {"mode": self.state.mode})

    def set_mode(self, mode: str) -> None:
        previous_mode = self.state.mode
        self.state.set_mode(mode)
        self.event_bus.publish(
            "state.mode_changed",
            {"previous_mode": previous_mode, "mode": self.state.mode},
        )

    def _register_core_handlers(self) -> None:
        self.event_bus.subscribe("system.start", self._log_start)
        self.event_bus.subscribe("system.heartbeat", self._log_heartbeat)
        self.event_bus.subscribe("system.shutdown", self._log_shutdown)
        self.event_bus.subscribe("state.mode_changed", self._log_mode_changed)

    def _log_start(self, payload: dict[str, Any]) -> None:
        self.logger.info(
            "%s starting in %s mode",
            payload["robot_name"],
            payload["mode"],
        )
        self.logger.info("Project root: %s", payload["root_dir"])

    def _log_heartbeat(self, payload: dict[str, Any]) -> None:
        self.logger.info(
            "Heartbeat mode=%s battery=%s",
            payload["mode"],
            payload["battery_percent"],
        )

    def _log_shutdown(self, payload: dict[str, Any]) -> None:
        self.logger.info("Nomad stopped from %s mode", payload["mode"])

    def _log_mode_changed(self, payload: dict[str, Any]) -> None:
        self.logger.info(
            "Mode changed: %s -> %s",
            payload["previous_mode"],
            payload["mode"],
        )
