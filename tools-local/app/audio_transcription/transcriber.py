import base64
import json
import urllib.request
import urllib.error


class AudioTranscriber:
    """Send audio to a local LLM endpoint (Ollama/vLLM/llama.cpp) for transcription."""

    @staticmethod
    def transcribe_ollama(endpoint: str, model: str, audio_bytes: bytes, filename: str) -> dict:
        """
        Ollama API: POST /api/generate with audio as base64 image field
        or POST /api/chat for multimodal models.
        """
        b64_audio = base64.b64encode(audio_bytes).decode("ascii")

        # Use chat endpoint for multimodal
        url = endpoint.rstrip("/") + "/api/chat"
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": f"Transcribe the following audio file ({filename}) accurately. Output only the transcription text, nothing else.",
                    "images": [b64_audio],
                }
            ],
            "stream": False,
        }

        return AudioTranscriber._post_json(url, payload, parser="ollama_chat")

    @staticmethod
    def transcribe_openai_compatible(endpoint: str, audio_bytes: bytes, filename: str) -> dict:
        """
        OpenAI-compatible /v1/audio/transcriptions endpoint
        (used by vLLM, llama.cpp with whisper models).
        """
        import mimetypes
        mime = mimetypes.guess_type(filename)[0] or "audio/mpeg"

        url = endpoint.rstrip("/") + "/v1/audio/transcriptions"

        # Build multipart form data manually
        boundary = "----AudioTranscriptionBoundary"
        body = b""

        # File field
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
        body += f"Content-Type: {mime}\r\n\r\n".encode()
        body += audio_bytes
        body += b"\r\n"

        # Model field
        body += f"--{boundary}\r\n".encode()
        body += b'Content-Disposition: form-data; name="model"\r\n\r\n'
        body += b"whisper-1\r\n"

        body += f"--{boundary}--\r\n".encode()

        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read().decode())
                return {"text": data.get("text", ""), "error": None}
        except urllib.error.HTTPError as e:
            return {"text": "", "error": f"HTTP {e.code}: {e.read().decode()[:500]}"}
        except Exception as e:
            return {"text": "", "error": str(e)}

    @staticmethod
    def transcribe_generic(endpoint: str, model: str, audio_bytes: bytes, filename: str) -> dict:
        """
        Generic endpoint: POST JSON with base64 audio.
        Works with custom servers that accept {"audio": base64, "model": model}.
        """
        b64_audio = base64.b64encode(audio_bytes).decode("ascii")

        url = endpoint.rstrip("/")
        payload = {
            "model": model,
            "audio": b64_audio,
            "filename": filename,
        }

        return AudioTranscriber._post_json(url, payload, parser="generic")

    @staticmethod
    def _post_json(url: str, payload: dict, parser: str) -> dict:
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            return {"text": "", "error": f"HTTP {e.code}: {e.read().decode()[:500]}"}
        except urllib.error.URLError as e:
            return {"text": "", "error": f"Connection error: {e.reason}"}
        except Exception as e:
            return {"text": "", "error": str(e)}

        if parser == "ollama_chat":
            msg = data.get("message", {})
            return {"text": msg.get("content", ""), "error": None}
        elif parser == "generic":
            return {"text": data.get("text", data.get("transcription", str(data))), "error": None}
        else:
            return {"text": str(data), "error": None}
