"""
Optional: fetch Gatsby page-data.json for classified doc URLs and record sample-code-loader keys.

This links documentation pages to sample bundle names (e.g. product-offers-request).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from discover import page_data_url_for_doc
from extract import walk_frontmatter, walk_page_data_for_loaders
from http_util import get_json, session


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", type=Path, default=Path("output"))
    ap.add_argument("--only-class", default="include_api_doc", help="Only process URLs with this class")
    ap.add_argument("--max", type=int, default=200)
    args = ap.parse_args()
    in_dir = args.in_dir

    classified = json.loads((in_dir / "crawl-urls-classified.json").read_text(encoding="utf-8"))
    sess = session()

    pages: list[dict] = []
    for row in classified.get("urls", []):
        if row.get("class") != args.only_class:
            continue
        if len(pages) >= args.max:
            break
        u = row["url"]
        try:
            pdata = get_json(sess, page_data_url_for_doc(u))
        except Exception as e:
            pages.append({"url": u, "error": str(e)})
            continue
        fm = walk_frontmatter(pdata)
        loaders = walk_page_data_for_loaders(pdata)
        pages.append(
            {
                "url": u,
                "title": fm.get("title"),
                "category": fm.get("category"),
                "tags": fm.get("tags"),
                "sample_code_loader_src": loaders,
            }
        )

    (in_dir / "page-sample-loaders.json").write_text(json.dumps({"pages": pages}, indent=2), encoding="utf-8")
    print(f"Wrote page-sample-loaders.json ({len(pages)} pages) -> {in_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
