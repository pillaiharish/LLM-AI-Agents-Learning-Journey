import math
import os
import subprocess


class MediaTokenEstimator:
    # --- Image methods ---

    @staticmethod
    def openai_tiles(width: int, height: int) -> int:
        """OpenAI vision token calculation: scale, tile, count."""
        # Scale so longest side <= 2048
        if max(width, height) > 2048:
            scale = 2048 / max(width, height)
            width = int(width * scale)
            height = int(height * scale)

        # Scale so shortest side <= 768
        if min(width, height) > 768:
            scale = 768 / min(width, height)
            width = int(width * scale)
            height = int(height * scale)

        tiles_x = math.ceil(width / 512)
        tiles_y = math.ceil(height / 512)
        return 85 + 170 * tiles_x * tiles_y

    @staticmethod
    def anthropic_pixels(width: int, height: int) -> int:
        """Anthropic: tokens ≈ (width * height) / 750"""
        return max(1, int((width * height) / 750))

    @staticmethod
    def google_fixed(width: int = 0, height: int = 0) -> int:
        """Google: fixed 258 tokens per image."""
        return 258

    @staticmethod
    def simplified_image(file_size_bytes: int) -> int:
        """Fallback: rough estimate based on file size."""
        # ~1 token per 100 bytes is a rough heuristic for images
        return max(1, file_size_bytes // 100)

    @staticmethod
    def estimate_image_tokens(
        file_path: str, method: str | None
    ) -> dict:
        """Estimate image tokens using provider-specific + simplified methods."""
        file_size = os.path.getsize(file_path)
        width, height = MediaTokenEstimator._get_image_dimensions(file_path)

        results = {"file_size_bytes": file_size, "width": width, "height": height}

        if method and width and height:
            method_map = {
                "openai_tiles": MediaTokenEstimator.openai_tiles,
                "anthropic_pixels": MediaTokenEstimator.anthropic_pixels,
                "google_fixed": MediaTokenEstimator.google_fixed,
            }
            fn = method_map.get(method)
            if fn:
                results["provider_tokens"] = fn(width, height)
                results["provider_method"] = method

        results["simplified_tokens"] = MediaTokenEstimator.simplified_image(file_size)
        return results

    @staticmethod
    def _get_image_dimensions(file_path: str) -> tuple[int, int]:
        try:
            from PIL import Image

            with Image.open(file_path) as img:
                return img.size
        except Exception:
            return (0, 0)

    # --- Audio methods ---

    @staticmethod
    def estimate_audio_tokens(
        file_path: str, method: str | None
    ) -> dict:
        """Estimate audio tokens: ~25 tokens/second."""
        file_size = os.path.getsize(file_path)
        duration = MediaTokenEstimator._get_audio_duration(file_path)

        if duration is None:
            # Fallback: estimate duration from file size (~16KB/s for mp3)
            duration = file_size / (16 * 1024)

        tokens = int(duration * 25)
        return {
            "file_size_bytes": file_size,
            "duration_seconds": round(duration, 2),
            "token_count": max(1, tokens),
            "method": method or "generic_audio",
        }

    @staticmethod
    def _get_audio_duration(file_path: str) -> float | None:
        # Try pydub first
        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0
        except Exception:
            pass

        # Try ffprobe
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "quiet",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    file_path,
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
        except Exception:
            pass

        return None
