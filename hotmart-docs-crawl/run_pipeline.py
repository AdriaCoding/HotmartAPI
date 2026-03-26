#!/usr/bin/env python3
"""
Run the full Hotmart docs extraction pipeline (network required).

Steps:
  1) discover  — sitemap (+ optional BFS), static-query hashes, download sq-*.json
  2) classify  — crawl-urls-classified.json
  3) extract   — endpoint-inventory-raw.json (from sample-code in static queries)
  4) validate  — endpoint-inventory.json + review file
  5) (optional) page_loaders — page-sample-loaders.json
  6) postman_extend — extend Postman collection
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], cwd: Path) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.check_call(cmd, cwd=str(cwd))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=Path("output"))
    ap.add_argument("--bfs", action="store_true", help="Pass --bfs to discover.py")
    ap.add_argument("--skip-page-loaders", action="store_true")
    ap.add_argument("--skip-postman", action="store_true")
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    discover_cmd = [
        sys.executable,
        str(here / "discover.py"),
        "--out-dir",
        str(out),
        "--fetch-sq",
    ]
    if args.bfs:
        discover_cmd.append("--bfs")

    _run(discover_cmd, here)
    _run([sys.executable, str(here / "classify.py"), "--in-dir", str(out)], here)

    if not args.skip_page_loaders:
        _run(
            [sys.executable, str(here / "page_loaders.py"), "--in-dir", str(out), "--max", "200"],
            here,
        )

    _run([sys.executable, str(here / "extract.py"), "--in-dir", str(out)], here)
    _run([sys.executable, str(here / "validate.py"), "--in-dir", str(out)], here)

    if not args.skip_postman:
        _run(
            [
                sys.executable,
                str(here / "postman_extend.py"),
                "--inventory",
                str(out / "endpoint-inventory.json"),
            ],
            here,
        )

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
