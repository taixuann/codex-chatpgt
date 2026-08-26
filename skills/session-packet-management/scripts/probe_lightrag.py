#!/usr/bin/env python3
"""Probe LightRAG availability without installing dependencies or indexing data."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", help="Optional LightRAG server URL to probe")
    args = parser.parse_args()
    result = {
        "engine": "lightrag",
        "status": "NOT_ASSESSED",
        "mode": "none",
        "evidence": "",
    }
    if args.base_url:
        url = args.base_url.rstrip("/") + "/health"
        try:
            request = Request(url, method="GET")
            with urlopen(request, timeout=5) as response:  # nosec B310: explicit operator URL
                result.update(status="PASS" if 200 <= response.status < 300 else "BLOCKED", mode="rest", evidence=f"HTTP {response.status} {url}")
        except (OSError, URLError) as exc:
            result.update(status="BLOCKED", mode="rest", evidence=f"{type(exc).__name__}: {exc}")
    elif importlib.util.find_spec("lightrag"):
        result.update(status="PASS", mode="sdk", evidence="lightrag importable; storage initialization not probed")
    else:
        result.update(status="NOT_ASSESSED", evidence="lightrag package unavailable and no server URL supplied")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
