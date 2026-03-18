import uuid


class SessionManager:
    """In-memory session store for Gemini chat conversations."""

    def __init__(self):
        self._sessions: dict[str, dict] = {}

    def create(self) -> str:
        sid = str(uuid.uuid4())
        self._sessions[sid] = {"history": [], "memory": True}
        return sid

    def get(self, sid: str) -> dict | None:
        return self._sessions.get(sid)

    def add_exchange(self, sid: str, user_parts: list, model_text: str):
        session = self._sessions.get(sid)
        if not session:
            return
        session["history"].append({"role": "user", "parts": user_parts})
        session["history"].append({"role": "model", "parts": [{"text": model_text}]})

    def get_history(self, sid: str) -> list:
        session = self._sessions.get(sid)
        if not session or not session["memory"]:
            return []
        return session["history"]

    def set_memory(self, sid: str, enabled: bool):
        session = self._sessions.get(sid)
        if session:
            session["memory"] = enabled

    def get_memory(self, sid: str) -> bool:
        session = self._sessions.get(sid)
        return session["memory"] if session else True

    def clear(self, sid: str):
        if sid in self._sessions:
            self._sessions[sid]["history"] = []

    def delete(self, sid: str):
        self._sessions.pop(sid, None)

    def list_sessions(self) -> list:
        return [
            {
                "id": sid,
                "message_count": len(s["history"]),
                "memory": s["memory"],
            }
            for sid, s in self._sessions.items()
        ]
