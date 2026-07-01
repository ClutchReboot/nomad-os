"""Tests for the event bus."""

import unittest

from nomad.core.event_bus import EventBus


class EventBusTest(unittest.TestCase):
    def test_publish_calls_subscriber(self) -> None:
        received: list[dict[str, str]] = []
        bus = EventBus()

        bus.subscribe("robot.ready", received.append)
        bus.publish("robot.ready", {"status": "ok"})

        self.assertEqual(received, [{"status": "ok"}])


if __name__ == "__main__":
    unittest.main()
