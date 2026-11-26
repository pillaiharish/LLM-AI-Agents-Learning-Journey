from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ProviderError(RuntimeError):
    """Raised when the local model provider cannot complete a request."""


@dataclass(frozen=True)
class ChatResult:
    content: str
    latency_ms: float | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class ChatProvider(Protocol):
    def chat(self, messages: list[dict[str, str]]) -> ChatResult: ...

