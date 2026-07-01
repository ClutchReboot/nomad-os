"""Conversation pipeline for text and voice interactions."""

from dataclasses import dataclass

from nomad.ai.brain import Brain
from nomad.core.event_bus import EventBus
from nomad.voice.text_to_speech import TextToSpeech


@dataclass(frozen=True)
class ConversationTurn:
    """A single user/Nomad exchange."""

    message: str
    response: str


class ConversationService:
    """Route user messages through the brain and speech output."""

    def __init__(
        self,
        brain: Brain | None = None,
        text_to_speech: TextToSpeech | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.brain = brain or Brain()
        self.text_to_speech = text_to_speech or TextToSpeech()
        self.event_bus = event_bus or EventBus()

    def handle_message(self, message: str) -> ConversationTurn:
        normalized_message = message.strip()
        if not normalized_message:
            raise ValueError("Message cannot be empty.")

        self.event_bus.publish(
            "conversation.user_message",
            {"message": normalized_message},
        )

        response = self.brain.respond(normalized_message)

        self.event_bus.publish(
            "conversation.nomad_response",
            {"message": normalized_message, "response": response},
        )
        self.text_to_speech.speak(response)

        return ConversationTurn(message=normalized_message, response=response)
