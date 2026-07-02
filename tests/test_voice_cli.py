"""Tests for the voice CLI flow."""

from unittest.mock import patch
import unittest

from nomad.voice import speech_to_text

from nomad.main import voice_chat
from nomad.voice.speech_to_text import SpeechToText


class StubSpeechToText:
    def __init__(self, transcripts: list[str]) -> None:
        self._transcripts = transcripts

    def listen_continuously(self) -> str:
        if not self._transcripts:
            raise AssertionError("No transcript left")
        return self._transcripts.pop(0)


class RecordingConversation:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def handle_message(self, message: str) -> object:
        self.messages.append(message)
        return type("Turn", (), {"message": message, "response": "ok"})()


class RecordingTextToSpeech:
    def __init__(self) -> None:
        self.spoken: list[str] = []

    def speak(self, text: str) -> None:
        self.spoken.append(text)


class VoiceCliTest(unittest.TestCase):
    def test_voice_chat_processes_a_transcript_and_stops(self) -> None:
        conversation = RecordingConversation()
        speech = StubSpeechToText(["Nomad hello", "Nomad quit"])
        output = RecordingTextToSpeech()

        voice_chat(
            conversation=conversation,
            speech_to_text=speech,
            text_to_speech=output,
            stop_after=1,
        )

        self.assertEqual(conversation.messages, ["hello"])

    def test_voice_chat_ignores_non_nomad_commands(self) -> None:
        conversation = RecordingConversation()
        speech = StubSpeechToText(["hello", "Nomad test", "Nomad quit"])
        output = RecordingTextToSpeech()

        voice_chat(
            conversation=conversation,
            speech_to_text=speech,
            text_to_speech=output,
            stop_after=2,
        )

        self.assertEqual(conversation.messages, ["test"])

    @patch("builtins.input", return_value="hello")
    def test_transcribe_falls_back_to_keyboard_input(self, _input) -> None:
        speech = SpeechToText()

        self.assertEqual(speech.transcribe(prompt=""), "hello")

    @patch("builtins.input", return_value="hello")
    def test_transcribe_falls_back_when_audio_backend_is_unavailable(
        self, _input
    ) -> None:
        def import_module(name: str):
            raise ImportError(name)

        with patch.object(speech_to_text, "import_module", side_effect=import_module):
            speech = SpeechToText()
            self.assertEqual(speech.transcribe(prompt=""), "hello")


if __name__ == "__main__":
    unittest.main()
