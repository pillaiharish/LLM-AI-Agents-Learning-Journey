import re
import subprocess


class NetworkScanner:
    @staticmethod
    def scan_devices() -> list:
        """Parse arp -a output to find local devices."""
        devices = []
        try:
            result = subprocess.run(
                ["arp", "-a"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode != 0:
                return devices

            for line in result.stdout.strip().split('\n'):
                # macOS format: hostname (ip) at mac on interface
                m = re.match(r'^(\S+)\s+\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+(\S+)', line)
                if m:
                    hostname = m.group(1) if m.group(1) != '?' else ''
                    devices.append({
                        "ip": m.group(2),
                        "mac": m.group(3),
                        "hostname": hostname,
                    })
        except Exception:
            pass
        return devices
