import os
import shutil


class StorageAnalyzer:
    @staticmethod
    def analyze(path: str = "/", max_items: int = 10) -> dict:
        # Disk usage
        usage = shutil.disk_usage(path)

        # Top paths by size
        top_paths = StorageAnalyzer._get_top_paths(path, max_items)

        return {
            "total": usage.total,
            "used": usage.used,
            "available": usage.free,
            "top_paths": top_paths,
        }

    @staticmethod
    def _get_top_paths(path: str, limit: int) -> list:
        entries = []
        try:
            for entry in os.scandir(path):
                if entry.name.startswith('.'):
                    continue
                try:
                    if entry.is_dir(follow_symlinks=False):
                        size = StorageAnalyzer._dir_size(entry.path)
                    else:
                        size = entry.stat(follow_symlinks=False).st_size
                    entries.append({"path": entry.path, "size": size})
                except (PermissionError, OSError):
                    continue
        except (PermissionError, OSError):
            pass

        entries.sort(key=lambda x: x["size"], reverse=True)
        return entries[:limit]

    @staticmethod
    def _dir_size(path: str, max_depth: int = 3) -> int:
        if max_depth <= 0:
            return 0
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.name.startswith('.'):
                    continue
                try:
                    if entry.is_dir(follow_symlinks=False):
                        total += StorageAnalyzer._dir_size(entry.path, max_depth - 1)
                    else:
                        total += entry.stat(follow_symlinks=False).st_size
                except (PermissionError, OSError):
                    continue
        except (PermissionError, OSError):
            pass
        return total
