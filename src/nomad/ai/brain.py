"""Robot decision-making."""

from collections.abc import Callable
import logging
from typing import Any

from nomad.ai.prompts import SYSTEM_PROMPT
from nomad.core.config import AppConfig, load_config


HttpPost = Callable[..., Any]


class Brain:
    """Choose responses and actions for Nomad."""

    def __init__(
        self,
        config: AppConfig | None = None,
        http_post: HttpPost | None = None,
    ) -> None:
        loaded_config = config or load_config()
        ai_settings = loaded_config.settings.get("ai", {})

        self.provider = str(ai_settings.get("provider", "lmstudio"))
        provider_settings = ai_settings.get(self.provider, {})
        if not isinstance(provider_settings, dict):
            provider_settings = {}

        self.model = str(provider_settings.get("model", "local-model"))
        self.base_url = str(
            provider_settings.get("base_url", "http://127.0.0.1:1234/v1")
        ).rstrip("/")
        self.timeout_seconds = float(provider_settings.get("timeout_seconds", 120))
        self.fallback_to_echo = bool(ai_settings.get("fallback_to_echo", True))
        self._http_post = http_post
        self._logger = logging.getLogger(__name__)

    def respond(self, message: str) -> str:
        try:
            if self.provider == "ollama":
                return self._respond_with_ollama(message)

            if self.provider in {"lmstudio", "openai_compatible"}:
                return self._respond_with_openai_compatible(message)

            return self._fallback_response(message)
        except Exception as exc:
            if self.fallback_to_echo:
                self._logger.warning(
                    "Local LLM provider %s failed; using echo fallback: %s",
                    self.provider,
                    exc,
                )
                return self._fallback_response(message)
            raise

    def _respond_with_ollama(self, message: str) -> str:
        post = self._http_post or self._requests_post
        response = post(
            f"{self.base_url}/chat",
            json={
                "model": self.model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message},
                ],
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()

        data = response.json()
        content = data.get("message", {}).get("content", "").strip()
        if not content:
            raise ValueError("Ollama returned an empty response.")

        return content

    def _respond_with_openai_compatible(self, message: str) -> str:
        post = self._http_post or self._requests_post
        response = post(
            f"{self.base_url}/chat/completions",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message},
                ],
                "temperature": 0.7,
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()

        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        content = content.strip()
        if not content:
            raise ValueError("LM Studio returned an empty response.")

        return content

    def _requests_post(self, *args: Any, **kwargs: Any) -> Any:
        try:
            import requests
        except ImportError as exc:
            raise RuntimeError("Install requests before using a local LLM.") from exc

        return requests.post(*args, **kwargs)

    def _fallback_response(self, message: str) -> str:
        return f"I heard: {message}"
