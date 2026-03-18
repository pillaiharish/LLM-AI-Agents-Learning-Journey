import json
import os
import tempfile

from core.file_processor import FileProcessor
from core.media import MediaTokenEstimator
from core.tokenizer import TokenCounter

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "models.json")


def _load_models() -> list[dict]:
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def _calculate_cost(tokens: int, cost_per_million: float | None) -> float | None:
    if cost_per_million is None:
        return None
    return round((tokens / 1_000_000) * cost_per_million, 6)


def _filter_models(models: list[dict], model_filter: str | None) -> list[dict]:
    if not model_filter:
        return models
    q = model_filter.lower()
    return [
        m
        for m in models
        if q in m["id"].lower()
        or q in m["name"].lower()
        or q in m["provider"].lower()
    ]


class TokenCalculator:
    @staticmethod
    def calculate_from_text(
        text: str, model_filter: str | None = None
    ) -> dict:
        models = _filter_models(_load_models(), model_filter)
        results = []
        for model in models:
            count_info = TokenCounter.count_for_model(text, model)
            tokens = count_info["token_count"]
            results.append(
                {
                    "model": model["name"],
                    "model_id": model["id"],
                    "provider": model["provider"],
                    "context_window": model["context_window"],
                    "tokens": tokens,
                    "method": count_info["method"],
                    "input_cost": _calculate_cost(
                        tokens, model["input_cost_per_million"]
                    ),
                    "cached_input_cost": _calculate_cost(
                        tokens, model["cached_input_cost_per_million"]
                    ),
                    "output_cost": _calculate_cost(
                        tokens, model["output_cost_per_million"]
                    ),
                }
            )

        word_count = len(text.split())
        char_count = len(text)
        return {
            "input_type": "text",
            "word_count": word_count,
            "char_count": char_count,
            "results": results,
        }

    @staticmethod
    def calculate_from_file(
        file_path: str, model_filter: str | None = None
    ) -> dict:
        filename = os.path.basename(file_path)
        file_type = FileProcessor.classify(filename)

        if file_type == "text":
            text = FileProcessor.extract_text(file_path)
            result = TokenCalculator.calculate_from_text(text, model_filter)
            result["input_type"] = "file"
            result["filename"] = filename
            result["file_type"] = file_type
            return result

        # Media files (image or audio)
        models = _filter_models(_load_models(), model_filter)
        results = []

        for model in models:
            if file_type == "image":
                method = model.get("image_token_method")
                estimate = MediaTokenEstimator.estimate_image_tokens(file_path, method)

                if "provider_tokens" in estimate:
                    tokens = estimate["provider_tokens"]
                    token_method = estimate["provider_method"]
                else:
                    tokens = estimate["simplified_tokens"]
                    token_method = "simplified (file size)"

                results.append(
                    {
                        "model": model["name"],
                        "model_id": model["id"],
                        "provider": model["provider"],
                        "context_window": model["context_window"],
                        "tokens": tokens,
                        "method": token_method,
                        "input_cost": _calculate_cost(
                            tokens, model["input_cost_per_million"]
                        ),
                        "cached_input_cost": _calculate_cost(
                            tokens, model["cached_input_cost_per_million"]
                        ),
                        "output_cost": _calculate_cost(
                            tokens, model["output_cost_per_million"]
                        ),
                        "media_details": {
                            "width": estimate.get("width"),
                            "height": estimate.get("height"),
                            "file_size_bytes": estimate.get("file_size_bytes"),
                        },
                    }
                )

            elif file_type == "audio":
                method = model.get("audio_token_method")
                if method is None:
                    results.append(
                        {
                            "model": model["name"],
                            "model_id": model["id"],
                            "provider": model["provider"],
                            "context_window": model["context_window"],
                            "tokens": None,
                            "method": "not supported",
                            "input_cost": None,
                            "cached_input_cost": None,
                            "output_cost": None,
                        }
                    )
                    continue

                estimate = MediaTokenEstimator.estimate_audio_tokens(
                    file_path, method
                )
                tokens = estimate["token_count"]
                results.append(
                    {
                        "model": model["name"],
                        "model_id": model["id"],
                        "provider": model["provider"],
                        "context_window": model["context_window"],
                        "tokens": tokens,
                        "method": estimate["method"],
                        "input_cost": _calculate_cost(
                            tokens, model["input_cost_per_million"]
                        ),
                        "cached_input_cost": _calculate_cost(
                            tokens, model["cached_input_cost_per_million"]
                        ),
                        "output_cost": _calculate_cost(
                            tokens, model["output_cost_per_million"]
                        ),
                        "media_details": {
                            "duration_seconds": estimate.get("duration_seconds"),
                            "file_size_bytes": estimate.get("file_size_bytes"),
                        },
                    }
                )

        return {
            "input_type": "file",
            "filename": filename,
            "file_type": file_type,
            "results": results,
        }

    @staticmethod
    def calculate_from_file_bytes(
        file_bytes: bytes,
        filename: str,
        model_filter: str | None = None,
    ) -> dict:
        ext = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            return TokenCalculator.calculate_from_file(tmp_path, model_filter)
        finally:
            os.unlink(tmp_path)

    @staticmethod
    def get_models() -> list[dict]:
        return _load_models()
