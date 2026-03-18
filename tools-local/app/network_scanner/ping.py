import subprocess


class PingTester:
    @staticmethod
    def ping(host: str, count: int = 3) -> str:
        try:
            result = subprocess.run(
                ["ping", "-c", str(count), host],
                capture_output=True, text=True, timeout=15,
            )
            return result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return f"Ping to {host} timed out"
        except Exception as e:
            return f"Error: {e}"
