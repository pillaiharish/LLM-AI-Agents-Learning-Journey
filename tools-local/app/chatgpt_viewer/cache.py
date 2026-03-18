import hashlib
import json
import os


class ConversationCache:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.cache_dir = os.path.join(data_dir, ".cache")
        self.cache_file = os.path.join(self.cache_dir, "processed.json")
        self.hash_file = os.path.join(self.cache_dir, "hash.txt")

    def get_cached(self) -> list | None:
        """Return cached data if source hasn't changed."""
        src = os.path.join(self.data_dir, "conversations.json")
        if not os.path.exists(src):
            return None

        current_hash = self._file_hash(src)
        if os.path.exists(self.hash_file) and os.path.exists(self.cache_file):
            with open(self.hash_file, "r") as f:
                stored_hash = f.read().strip()
            if stored_hash == current_hash:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        return None

    def save(self, data: list):
        """Save processed data to cache."""
        os.makedirs(self.cache_dir, exist_ok=True)

        src = os.path.join(self.data_dir, "conversations.json")
        current_hash = self._file_hash(src) if os.path.exists(src) else ""

        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        with open(self.hash_file, "w") as f:
            f.write(current_hash)

    def invalidate(self):
        """Force reprocessing on next load."""
        if os.path.exists(self.hash_file):
            os.remove(self.hash_file)

    @staticmethod
    def _file_hash(path: str) -> str:
        h = hashlib.md5()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
