from __future__ import annotations

import json

import httpx
import pytest

from prompt_lab.config import Settings
from prompt_lab.ollama import OllamaClient, validate_ollama_url
from prompt_lab.provider import ProviderError


def settings(url: str = "http://localhost:11434") -> Settings:
    return Settings(
        url=url,
        model="qwen3.5:9b",
        temperature=0,
        seed=12345,
        num_predict=2048,
        timeout_seconds=5,
    )


def test_chat_builds_native_ollama_request() -> None:
    captured: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/chat"
        captured.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "message": {"role": "assistant", "content": "raw output\n"},
                "prompt_eval_count": 12,
                "eval_count": 3,
            },
        )

    client = OllamaClient(settings(), transport=httpx.MockTransport(handler))
    try:
        result = client.chat([{"role": "user", "content": "hello"}])
    finally:
        client.close()

    assert result.content == "raw output\n"
    assert result.prompt_tokens == 12
    assert result.completion_tokens == 3
    assert captured == [
        {
            "model": "qwen3.5:9b",
            "messages": [{"role": "user", "content": "hello"}],
            "stream": False,
            "think": False,
            "options": {"temperature": 0, "seed": 12345, "num_predict": 2048},
        }
    ]
    assert "format" not in captured[0]
    assert "tools" not in captured[0]


def test_retries_once_without_unsupported_think() -> None:
    payloads: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payloads.append(json.loads(request.content))
        if len(payloads) == 1:
            return httpx.Response(400, text="this model does not support thinking")
        return httpx.Response(200, json={"message": {"content": "OK"}})

    client = OllamaClient(settings(), transport=httpx.MockTransport(handler))
    try:
        assert client.chat([{"role": "user", "content": "test"}]).content == "OK"
    finally:
        client.close()
    assert len(payloads) == 2
    assert payloads[0]["think"] is False
    assert "think" not in payloads[1]


def test_does_not_retry_unrelated_error() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(500, text="server error")

    client = OllamaClient(settings(), transport=httpx.MockTransport(handler))
    with pytest.raises(ProviderError, match="HTTP 500"):
        client.chat([{"role": "user", "content": "test"}])
    client.close()
    assert calls == 1


@pytest.mark.parametrize(
    "url",
    [
        "https://localhost:11434",
        "http://example.com:11434",
        "http://0.0.0.0:11434",
        "http://user:pass@localhost:11434",
        "http://localhost:11434/api",
        "http://localhost:11434?token=value",
    ],
)
def test_rejects_nonlocal_or_unsafe_urls(url: str) -> None:
    with pytest.raises(ProviderError):
        validate_ollama_url(url)


@pytest.mark.parametrize(
    "url",
    ["http://localhost:11434", "http://127.0.0.1:11434", "http://[::1]:11434/"],
)
def test_accepts_loopback_urls(url: str) -> None:
    assert validate_ollama_url(url).startswith("http://")


def test_lists_installed_models() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"models": [{"name": "qwen3.5:9b"}]})
    )
    client = OllamaClient(settings(), transport=transport)
    try:
        assert client.installed_models() == ["qwen3.5:9b"]
    finally:
        client.close()

