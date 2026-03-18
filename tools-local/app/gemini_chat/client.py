import base64
import json
import mimetypes
import urllib.request
import urllib.error


GEMINI_MODELS = [
    {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash"},
    {"id": "gemini-2.0-pro", "name": "Gemini 2.0 Pro"},
    {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro"},
    {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash"},
]


class GeminiClient:
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    @staticmethod
    def send_message(
        api_key: str,
        model: str,
        message: str,
        history: list | None = None,
        files: list | None = None,
    ) -> dict:
        """
        Send a message to Gemini API.

        history: list of {"role": "user"|"model", "parts": [{"text": "..."}]}
        files: list of {"mime_type": str, "data": str (base64)}
        Returns: {"text": str, "usage": dict}
        """
        contents = []

        # Add conversation history if memory is on
        if history:
            contents.extend(history)

        # Build current user message parts
        parts = []

        # Add file parts first
        if files:
            for f in files:
                parts.append({
                    "inline_data": {
                        "mime_type": f["mime_type"],
                        "data": f["data"],
                    }
                })

        parts.append({"text": message})
        contents.append({"role": "user", "parts": parts})

        url = f"{GeminiClient.BASE_URL}/{model}:generateContent?key={api_key}"

        payload = json.dumps({"contents": contents}).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            try:
                err = json.loads(body)
                msg = err.get("error", {}).get("message", body)
            except json.JSONDecodeError:
                msg = body
            raise RuntimeError(f"Gemini API error ({e.code}): {msg}")

        # Extract response text
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("No response from Gemini")

        resp_parts = candidates[0].get("content", {}).get("parts", [])
        resp_text = "\n".join(p.get("text", "") for p in resp_parts if "text" in p)

        usage = data.get("usageMetadata", {})

        return {
            "text": resp_text,
            "usage": {
                "prompt_tokens": usage.get("promptTokenCount", 0),
                "response_tokens": usage.get("candidatesTokenCount", 0),
                "total_tokens": usage.get("totalTokenCount", 0),
            },
        }

    @staticmethod
    def file_to_part(file_bytes: bytes, filename: str) -> dict:
        """Convert uploaded file bytes to a Gemini inline_data part."""
        mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        b64 = base64.b64encode(file_bytes).decode("ascii")
        return {"mime_type": mime, "data": b64}
