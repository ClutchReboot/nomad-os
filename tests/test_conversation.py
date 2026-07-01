"""Tests for the conversation pipeline."""

import unittest

from nomad.core.conversation import ConversationService
from nomad.core.event_bus import EventBus


class EchoBrain:
    def respond(self, message: str) -> str:
        return f"I heard: {message}"


class RecordingSpeech:
    def __init__(self) -> None:
        self.spoken: list[str] = []

    def speak(self, text: str) -> None:
        self.spoken.append(text)


class ConversationServiceTest(unittest.TestCase):
    def test_handle_message_returns_response_and_speaks(self) -> None:
        speech = RecordingSpeech()
        conversation = ConversationService(
            brain=EchoBrain(),
            text_to_speech=speech,
        )

        turn = conversation.handle_message(" hello ")

        self.assertEqual(turn.message, "hello")
        self.assertEqual(turn.response, "I heard: hello")
        self.assertEqual(speech.spoken, ["I heard: hello"])

    def test_handle_message_publishes_events(self) -> None:
        events: list[tuple[str, dict[str, str]]] = []
        event_bus = EventBus()
        event_bus.subscribe(
            "conversation.user_message",
            lambda payload: events.append(("user", payload)),
        )
        event_bus.subscribe(
            "conversation.nomad_response",
            lambda payload: events.append(("nomad", payload)),
        )

        conversation = ConversationService(
            brain=EchoBrain(),
            text_to_speech=RecordingSpeech(),
            event_bus=event_bus,
        )

        conversation.handle_message("status")

        self.assertEqual(
            events,
            [
                ("user", {"message": "status"}),
                (
                    "nomad",
                    {"message": "status", "response": "I heard: status"},
                ),
            ],
        )

    def test_handle_message_rejects_empty_messages(self) -> None:
        conversation = ConversationService(
            brain=EchoBrain(),
            text_to_speech=RecordingSpeech(),
        )

        with self.assertRaises(ValueError):
            conversation.handle_message(" ")


if __name__ == "__main__":
    unittest.main()
