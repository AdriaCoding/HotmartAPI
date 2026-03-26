"""
Discover doc URLs (sitemap + optional BFS), fetch Gatsby static-query hashes,
and write crawl-urls.json + static-query manifest.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from config import DOCS_ORIGIN, DOCS_PREFIX, EN_DOCS_BASE, PAGE_DATA_JSON_TMPL, SITEMAP_EN, STATIC_QUERY_JSON_TMPL
from http_util import get_json, get_text, session


def _abs_docs_url(href: str) -> str | None:
    if not href or href.startswith("#") or href.startswith("mailto:"):
        return None
    u = urljoin(EN_DOCS_BASE + "/", href)
    p = urlparse(u)
    if p.scheme not in ("http", "https"):
        return None
    if p.netloc != urlparse(DOCS_ORIGIN).netloc:
        return None
    if not p.path.startswith(f"{DOCS_PREFIX}/en/"):
        return None
    if p.path.endswith(".json") or p.path.endswith(".js"):
        return None
    return u.split("#", 1)[0].rstrip("/") + "/"


def _parse_sitemap(xml: str) -> list[str]:
    urls: list[str] = []
    for m in re.finditer(r"<loc>\s*([^<]+)\s*</loc>", xml):
        urls.append(m.group(1).strip())
    return urls


def _doc_url_to_page_data_path(doc_url: str) -> str:
    """https://developers.hotmart.com/docs/en/start/foo/ -> /en/start/foo/page-data.json"""
    p = urlparse(doc_url)
    path = p.path.rstrip("/")
    if not path.startswith(f"{DOCS_PREFIX}/"):
        raise ValueError(f"Unexpected doc URL: {doc_url}")
    rel = path[len(DOCS_PREFIX) :]  # /en/start/foo
    return f"{rel}/page-data.json"


def page_data_url_for_doc(doc_url: str) -> str:
    p = urlparse(doc_url)
    path = p.path.rstrip("/")
    rel = path[len(DOCS_PREFIX) :] if path.startswith(DOCS_PREFIX) else path
    return PAGE_DATA_JSON_TMPL.format(rel_path=rel + "/")


def bfs_seed_urls(sess, start_url: str, max_pages: int) -> list[str]:
    seen: set[str] = set()
    queue: list[str] = [start_url.rstrip("/") + "/"]
    out: list[str] = []
    while queue and len(out) < max_pages:
        u = queue.pop(0)
        if u in seen:
            continue
        seen.add(u)
        try:
            html = get_text(sess, u)
        except Exception:
            continue
        out.append(u)
        soup = BeautifulSoup(html, "lxml")
        for a in soup.find_all("a", href=True):
            child = _abs_docs_url(a["href"])
            if child and child not in seen:
                queue.append(child)
    return out


def collect_static_query_hashes(sess, doc_urls: list[str], sample: int) -> list[str]:
    hashes: set[str] = set()
    for u in doc_urls[:sample]:
        try:
            pdata = get_json(sess, page_data_url_for_doc(u))
        except Exception:
            continue
        hs = pdata.get("staticQueryHashes") or []
        for h in hs:
            hashes.add(str(h))
    return sorted(hashes)


def main() -> int:
    ap = argparse.ArgumentParser(description="Discover Hotmart /docs/en URLs and static-query hashes.")
    ap.add_argument("--out-dir", type=Path, default=Path("output"), help="Output directory")
    ap.add_argument("--bfs", action="store_true", help="Also run BFS from the English docs home")
    ap.add_argument("--bfs-max", type=int, default=80, help="Max pages to crawl via BFS")
    ap.add_argument("--hash-sample", type=int, default=25, help="How many doc URLs to fetch page-data for hash discovery")
    ap.add_argument("--fetch-sq", action="store_true", help="Download each static-query JSON into out-dir as sq-<hash>.json")
    args = ap.parse_args()

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    sess = session()
    sitemap_xml = get_text(sess, SITEMAP_EN)
    sitemap_urls = _parse_sitemap(sitemap_xml)

    urls = list(dict.fromkeys(sitemap_urls))
    if args.bfs:
        bfs_urls = bfs_seed_urls(sess, EN_DOCS_BASE + "/", args.bfs_max)
        urls = list(dict.fromkeys(urls + bfs_urls))

    hashes = collect_static_query_hashes(sess, urls, args.hash_sample)

    manifest = {
        "generated_by": "discover.py",
        "sitemap": SITEMAP_EN,
        "static_query_hashes": hashes,
        "static_query_url_template": STATIC_QUERY_JSON_TMPL,
    }
    (out_dir / "static-query-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if args.fetch_sq:
        for h in hashes:
            url = STATIC_QUERY_JSON_TMPL.format(hash=h)
            try:
                doc = get_json(sess, url)
                (out_dir / f"sq-{h}.json").write_text(json.dumps(doc), encoding="utf-8")
            except Exception as e:
                print(f"WARN: failed to fetch {url}: {e}", file=sys.stderr)

    rows: list[dict[str, Any]] = []
    for u in urls:
        p = urlparse(u).path
        rows.append({"url": u, "path": p})

    (out_dir / "crawl-urls.json").write_text(json.dumps({"urls": rows}, indent=2), encoding="utf-8")

    print(f"Wrote {len(rows)} URLs and {len(hashes)} static-query hashes to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
