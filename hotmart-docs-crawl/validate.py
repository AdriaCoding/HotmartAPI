"""
Deduplicate extracted endpoints and emit endpoint-inventory.json + review file.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def _norm_path(p: str) -> str:
    # Normalize whitespace; keep :param style from docs
    return re.sub(r"\s+", "", p.strip())


def _confidence(path_template: str) -> str:
    if "{" in path_template and ":" in path_template:
        return "medium"
    if "/api/v" in path_template:
        return "high"
    return "medium"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", type=Path, default=Path("output"))
    ap.add_argument("--out-dir", type=Path, default=None)
    args = ap.parse_args()
    in_dir = args.in_dir
    out_dir = args.out_dir or in_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_path = in_dir / "endpoint-inventory-raw.json"
    if not raw_path.exists():
        print("Missing endpoint-inventory-raw.json — run extract.py first", file=sys.stderr)
        return 2

    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = list(raw.get("endpoints") or [])

    by_key: dict[tuple[str, str], dict[str, Any]] = {}

    for r in rows:
        method = str(r.get("method", "")).upper()
        path_t = _norm_path(str(r.get("path_template", "")))
        if not method or not path_t.startswith("/"):
            continue
        key = (method, path_t)
        entry = {
            "method": method,
            "path_template": path_t,
            "confidence": _confidence(path_t),
            "sources": sorted({str(r.get("source") or "unknown")}),
            "provenance": {"static_query_sample_code": True},
        }
        if key not in by_key:
            by_key[key] = entry
        else:
            # merge sources
            prev = by_key[key]
            prev_sources = set(prev.get("sources") or [])
            prev_sources.update(entry.get("sources") or [])
            prev["sources"] = sorted(prev_sources)

    inventory = {
        "generated_by": "validate.py",
        "endpoints": [by_key[k] for k in sorted(by_key.keys(), key=lambda x: (x[1], x[0]))],
    }
    (out_dir / "endpoint-inventory.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")

    # Attach named nodes summary as review hints
    named = raw.get("named_request_nodes") or []
    review = {
        "named_request_nodes_count": len(named),
        "notes": [
            "Paths come from Hotmart Gatsby sample-code blocks; verify against runtime OpenAPI where discrepancies exist.",
        ],
    }
    (out_dir / "endpoint-inventory-review.json").write_text(json.dumps(review, indent=2), encoding="utf-8")

    print(f"Deduped {len(inventory['endpoints'])} endpoints -> {out_dir / 'endpoint-inventory.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
