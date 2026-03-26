"""
Classify discovered URLs into buckets (exclude tutorials, include v1 API docs, etc.).
Reads crawl-urls.json, writes crawl-urls-classified.json.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from config import INCLUDE_DOC_PATH_REGEX


def classify(url: str) -> str:
    if "/tutorials/" in url:
        return "exclude_tutorial"
    if "/tos/" in url.lower():
        return "exclude_tos"
    if re.search(INCLUDE_DOC_PATH_REGEX, urlparse_path(url)):
        return "include_api_doc"
    if "/docs/en/start/" in url:
        return "include_start_guide"
    return "manual_review"


def urlparse_path(url: str) -> str:
    # https://x/docs/en/foo -> /docs/en/foo
    from urllib.parse import urlparse

    return urlparse(url).path.rstrip("/") + "/"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", type=Path, default=Path("output"))
    ap.add_argument("--out-dir", type=Path, default=None)
    args = ap.parse_args()
    in_dir = args.in_dir
    out_dir = args.out_dir or in_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads((in_dir / "crawl-urls.json").read_text(encoding="utf-8"))
    rows_out: list[dict[str, Any]] = []
    for row in data.get("urls", []):
        u = row["url"]
        bucket = classify(u)
        rows_out.append({**row, "class": bucket})

    (out_dir / "crawl-urls-classified.json").write_text(json.dumps({"urls": rows_out}, indent=2), encoding="utf-8")
    print(f"Classified {len(rows_out)} URLs -> {out_dir / 'crawl-urls-classified.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
