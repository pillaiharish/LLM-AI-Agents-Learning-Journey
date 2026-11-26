from __future__ import annotations

import os

import pytest

from prompt_lab.config import load_settings
from prompt_lab.ollama import OllamaClient


@pytest.mark.integration
@pytest.mark.skipif(
    os.environ.get("RUN_OLLAMA_INTEGRATION") != "1",
    reason="set RUN_OLLAMA_INTEGRATION=1 to use local Ollama",
)
def test_local_ollama_generation() -> None:
    client = OllamaClient(load_settings())
    try:
        result = client.chat([{"role": "user", "content": "Reply with exactly OK."}])
    finally:
        client.close()
    assert result.content

