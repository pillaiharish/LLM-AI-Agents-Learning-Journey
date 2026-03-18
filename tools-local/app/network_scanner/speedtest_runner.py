import time
import urllib.request
import subprocess


class SpeedTestRunner:
    _DOWNLOAD_URL = "https://speed.cloudflare.com/__down?bytes=25000000"  # 25 MB
    _UPLOAD_URL   = "https://speed.cloudflare.com/__up"
    _PING_HOST    = "1.1.1.1"
    _HEADERS      = {"User-Agent": "Mozilla/5.0"}

    @staticmethod
    def _ping() -> float:
        try:
            out = subprocess.run(
                ["ping", "-c", "4", SpeedTestRunner._PING_HOST],
                capture_output=True, text=True, timeout=10
            ).stdout
            for line in out.splitlines():
                if "avg" in line or "average" in line:
                    # macOS/Linux: "round-trip min/avg/max/stddev = 10/12/14/1 ms"
                    return round(float(line.split("=")[-1].strip().split("/")[1]), 1)
        except Exception:
            pass
        return 0.0

    @staticmethod
    def _download() -> float:
        req = urllib.request.Request(SpeedTestRunner._DOWNLOAD_URL,
                                     headers=SpeedTestRunner._HEADERS)
        t0 = time.monotonic()
        with urllib.request.urlopen(req, timeout=30) as r:
            size = len(r.read())
        return round((size * 8) / ((time.monotonic() - t0) * 1_000_000), 2)

    @staticmethod
    def _upload() -> float:
        payload = b"0" * 5_000_000  # 5 MB
        req = urllib.request.Request(
            SpeedTestRunner._UPLOAD_URL, data=payload, method="POST",
            headers={**SpeedTestRunner._HEADERS,
                     "Content-Type": "application/octet-stream"}
        )
        t0 = time.monotonic()
        with urllib.request.urlopen(req, timeout=30) as r:
            r.read()
        return round((len(payload) * 8) / ((time.monotonic() - t0) * 1_000_000), 2)

    @staticmethod
    def run() -> dict:
        try:
            return {
                "download": SpeedTestRunner._download(),
                "upload":   SpeedTestRunner._upload(),
                "ping":     SpeedTestRunner._ping(),
                "server":   "Cloudflare (speed.cloudflare.com)",
            }
        except Exception as e:
            return {"error": str(e)}
