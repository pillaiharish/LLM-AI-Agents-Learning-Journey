from __future__ import annotations

import time
from urllib.parse import urlsplit

import httpx

from .config import Settings
from .provider import ChatResult, ProviderError


_LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}


def validate_ollama_url(url: str) -> str:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in _LOOPBACK_HOSTS
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
    ):
        raise ProviderError(
            "Ollama URL must be a plain loopback HTTP URL such as "
            "http://localhost:11434"
        )
    try:
        parsed.port
    except ValueError as exc:
        raise ProviderError(f"Invalid Ollama URL: {exc}") from exc
    return url.rstrip("/")


class OllamaClient:
    def __init__(
        self,
        settings: Settings,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.settings = settings
        self.base_url = validate_ollama_url(settings.url)
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=settings.timeout_seconds,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def installed_models(self) -> list[str]:
        response = self._request("GET", "/api/tags")
        try:
            return [str(model["name"]) for model in response.json().get("models", [])]
        except (ValueError, TypeError, KeyError) as exc:
            raise ProviderError("Ollama returned an invalid /api/tags response") from exc

    def chat(self, messages: list[dict[str, str]]) -> ChatResult:
        payload = {
            "model": self.settings.model,
            "messages": messages,
            "stream": False,
            "think": False,
            "options": {
                "temperature": self.settings.temperature,
                "seed": self.settings.seed,
                "num_predict": self.settings.num_predict,
            },
        }
        started = time.perf_counter()
        response = self._request("POST", "/api/chat", json=payload, allow_error=True)
        if self._think_is_unsupported(response):
            payload.pop("think")
            response = self._request("POST", "/api/chat", json=payload, allow_error=True)
        self._raise_for_status(response)
        latency_ms = (time.perf_counter() - started) * 1000
        try:
            body = response.json()
            content = body["message"]["content"]
            if not isinstance(content, str):
                raise TypeError("message.content is not text")
        except (ValueError, TypeError, KeyError) as exc:
            raise ProviderError("Ollama returned an invalid /api/chat response") from exc
        return ChatResult(
            content=content,
            latency_ms=latency_ms,
            prompt_tokens=_optional_int(body.get("prompt_eval_count")),
            completion_tokens=_optional_int(body.get("eval_count")),
        )

    def _request(self, method: str, path: str, **kwargs: object) -> httpx.Response:
        allow_error = bool(kwargs.pop("allow_error", False))
        try:
            response = self._client.request(method, path, **kwargs)
        except httpx.HTTPError as exc:
            raise ProviderError(
                f"Cannot reach local Ollama at {self.base_url}: {exc}"
            ) from exc
        if not allow_error:
            self._raise_for_status(response)
        return response

    @staticmethod
    def _think_is_unsupported(response: httpx.Response) -> bool:
        if response.status_code not in (400, 422):
            return False
        text = response.text.lower()
        return "think" in text and any(
            marker in text
            for marker in (
                "unsupported",
                "not support",
                "unknown",
                "unrecognized",
                "invalid",
                "not allowed",
            )
        )

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.is_success:
            return
        detail = response.text.strip().replace("\n", " ")[:300]
        raise ProviderError(
            f"Ollama request failed with HTTP {response.status_code}: {detail}"
        )


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) else None

