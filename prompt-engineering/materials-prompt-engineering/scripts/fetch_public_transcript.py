from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlsplit

import httpx


ALLOWED_HOST = "raw.githubusercontent.com"
ALLOWED_PREFIX = "/BetaNYC/hearings-transcripts/"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download one optional BetaNYC transcript")
    parser.add_argument("--url", required=True, help="Raw GitHub URL from BetaNYC/hearings-transcripts")
    parser.add_argument("--output-name", required=True, help="Safe local filename without a directory")
    return parser.parse_args()


def validate_source(url: str, output_name: str) -> None:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST or not parsed.path.startswith(ALLOWED_PREFIX):
        raise ValueError("URL must be raw HTTPS content from BetaNYC/hearings-transcripts")
    if Path(output_name).name != output_name or output_name in {"", ".", ".."}:
        raise ValueError("output-name must be one filename without directories")


def fetch(url: str, output_name: str, destination: Path) -> tuple[Path, Path]:
    validate_source(url, output_name)
    destination.mkdir(parents=True, exist_ok=True)
    response = httpx.get(url, timeout=60, follow_redirects=False)
    response.raise_for_status()
    transcript_path = destination / output_name
    transcript_path.write_bytes(response.content)
    provenance_path = destination / f"{output_name}.provenance.json"
    provenance = {
        "source_url": url,
        "repository": "BetaNYC/hearings-transcripts",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "license": "CC BY 4.0",
    }
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    return transcript_path, provenance_path


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent.parent
    try:
        transcript, provenance = fetch(args.url, args.output_name, root / "data" / "external")
    except (ValueError, httpx.HTTPError, OSError) as exc:
        print(f"error: {exc}")
        return 1
    print(f"Saved {transcript}")
    print(f"Saved {provenance}")
    print("Review and anonymize the material before deriving any committed exercise.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

