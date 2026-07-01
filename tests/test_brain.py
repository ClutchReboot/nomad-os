"""Tests for Nomad's LLM brain."""

from pathlib import Path
import unittest
import unittest.mock

from nomad.ai.brain import Brain
from nomad.core.config import AppConfig


class FakeResponse:
    def __init__(self, data: dict) -> None:
        self._data = data

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._data


class BrainTest(unittest.TestCase):
    def test_respond_uses_lmstudio_chat_completions_api(self) -> None:
        calls: list[dict] = []

        def post(url: str, **kwargs) -> FakeResponse:
            calls.append({"url": url, **kwargs})
            return FakeResponse(
                {"choices": [{"message": {"content": "Hello from LM Studio."}}]}
            )

        brain = Brain(config=_lmstudio_config(), http_post=post)

        response = brain.respond("hello")

        self.assertEqual(response, "Hello from LM Studio.")
        self.assertEqual(calls[0]["url"], "http://lmstudio.test/v1/chat/completions")
        self.assertEqual(calls[0]["json"]["model"], "local-test")
        self.assertEqual(calls[0]["json"]["messages"][-1]["content"], "hello")

    def test_respond_uses_ollama_chat_api(self) -> None:
        calls: list[dict] = []

        def post(url: str, **kwargs) -> FakeResponse:
            calls.append({"url": url, **kwargs})
            return FakeResponse({"message": {"content": "Hello from Nomad."}})

        brain = Brain(config=_ollama_config(), http_post=post)

        response = brain.respond("hello")

        self.assertEqual(response, "Hello from Nomad.")
        self.assertEqual(calls[0]["url"], "http://ollama.test/api/chat")
        self.assertEqual(calls[0]["json"]["model"], "tiny-test")
        self.assertEqual(calls[0]["json"]["messages"][-1]["content"], "hello")

    @unittest.mock.patch("nomad.ai.brain.logging.getLogger")
    def test_respond_falls_back_when_llm_is_unavailable(self, get_logger) -> None:
        def post(url: str, **kwargs) -> FakeResponse:
            raise ConnectionError("not running")

        brain = Brain(config=_lmstudio_config(), http_post=post)

        self.assertEqual(brain.respond("hello"), "I heard: hello")


def _lmstudio_config() -> AppConfig:
    return AppConfig(
        settings={
            "ai": {
                "provider": "lmstudio",
                "fallback_to_echo": True,
                "lmstudio": {
                    "model": "local-test",
                    "base_url": "http://lmstudio.test/v1",
                    "timeout_seconds": 1,
                },
            }
        },
        devices={},
        secrets={},
        root_dir=Path.cwd(),
    )


def _ollama_config() -> AppConfig:
    return AppConfig(
        settings={
            "ai": {
                "provider": "ollama",
                "fallback_to_echo": True,
                "ollama": {
                    "model": "tiny-test",
                    "base_url": "http://ollama.test/api",
                    "timeout_seconds": 1,
                },
            }
        },
        devices={},
        secrets={},
        root_dir=Path.cwd(),
    )


if __name__ == "__main__":
    unittest.main()
