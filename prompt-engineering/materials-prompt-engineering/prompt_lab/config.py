from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import tomllib


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class ConfigError(ValueError):
    """Raised when project configuration is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    url: str
    model: str
    temperature: float
    seed: int
    num_predict: int
    timeout_seconds: float

    def with_overrides(
        self,
        *,
        url: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
    ) -> "Settings":
        return replace(
            self,
            url=url if url is not None else self.url,
            model=model if model is not None else self.model,
            temperature=temperature if temperature is not None else self.temperature,
        )


def load_settings(path: Path | None = None) -> Settings:
    config_path = path or PROJECT_ROOT / "prompt_lab.toml"
    try:
        with config_path.open("rb") as config_file:
            values = tomllib.load(config_file)["ollama"]
        return Settings(
            url=str(values["url"]),
            model=str(values["model"]),
            temperature=float(values["temperature"]),
            seed=int(values["seed"]),
            num_predict=int(values["num_predict"]),
            timeout_seconds=float(values["timeout_seconds"]),
        )
    except (OSError, KeyError, TypeError, ValueError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"Cannot load {config_path}: {exc}") from exc

