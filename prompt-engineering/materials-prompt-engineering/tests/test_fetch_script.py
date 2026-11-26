from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from prompt_lab.config import PROJECT_ROOT


def load_script():
    path = PROJECT_ROOT / "scripts" / "fetch_public_transcript.py"
    spec = importlib.util.spec_from_file_location("fetch_public_transcript", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fetcher_allows_only_known_raw_source() -> None:
    script = load_script()
    script.validate_source(
        "https://raw.githubusercontent.com/BetaNYC/hearings-transcripts/main/sample.txt",
        "sample.txt",
    )
    with pytest.raises(ValueError):
        script.validate_source("https://example.com/sample.txt", "sample.txt")
    with pytest.raises(ValueError):
        script.validate_source(
            "https://raw.githubusercontent.com/BetaNYC/hearings-transcripts/main/sample.txt",
            "../sample.txt",
        )

