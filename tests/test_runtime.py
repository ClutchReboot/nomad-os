"""Tests for the core runtime lifecycle."""

from pathlib import Path
import unittest

from nomad.core.config import AppConfig
from nomad.core.runtime import RobotRuntime


class RobotRuntimeTest(unittest.TestCase):
    def test_runtime_start_tick_stop(self) -> None:
        runtime = RobotRuntime(
            AppConfig(
                settings={
                    "robot": {"name": "Test Nomad"},
                    "runtime": {"initial_mode": "idle", "heartbeat_seconds": 0.01},
                    "logging": {"level": "CRITICAL"},
                },
                devices={},
                secrets={},
                root_dir=Path.cwd(),
            )
        )

        runtime.start()
        runtime.tick()
        runtime.stop()

        self.assertFalse(runtime.state.running)
        self.assertIsNotNone(runtime.state.started_at)
        self.assertIsNotNone(runtime.state.last_heartbeat_at)
        self.assertEqual(runtime.state.metadata["robot_name"], "Test Nomad")


if __name__ == "__main__":
    unittest.main()
