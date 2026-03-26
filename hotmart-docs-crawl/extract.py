"""
Extract API operations from Gatsby static-query JSON (sample-code blocks).

Hotmart embeds request samples in static query chunks under nodes named like
`product-offers-request` with `sample-code` elements:
  properties: { method: GET, title: /products/api/v1/...  }

This is more reliable than scraping rendered HTML.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from config import HTTP_METHODS, STATIC_QUERY_JSON_TMPL
from http_util import get_json, session


def _walk(obj: Any, visit) -> None:
    if isinstance(obj, dict):
        visit(obj)
        for v in obj.values():
            _walk(v, visit)
    elif isinstance(obj, list):
        for x in obj:
            _walk(x, visit)


def walk_page_data_for_loaders(page_data: dict) -> list[str]:
    """Return sample-code-loader src keys from markdownRemark htmlAst."""
    out: list[str] = []

    def visit(node: dict) -> None:
        if node.get("type") != "element":
            return
        if node.get("tagName") != "sample-code-loader":
            return
        src = (node.get("properties") or {}).get("src")
        if isinstance(src, str) and src:
            out.append(src)

    try:
        ast = page_data["result"]["data"]["markdownRemark"]["htmlAst"]
        _walk(ast, visit)
    except Exception:
        pass
    return out


def walk_frontmatter(page_data: dict) -> dict[str, Any]:
    try:
        return dict(page_data["result"]["data"]["markdownRemark"].get("frontmatter") or {})
    except Exception:
        return {}


def extract_endpoint_samples(static_query_doc: dict) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Returns:
      - endpoints: unique (method, path_template) from sample-code tags
      - named_nodes: *-request nodes with optional absolutePath for provenance
    """
    endpoints: list[dict[str, Any]] = []
    named_nodes: list[dict[str, Any]] = []

    def visit(node: dict) -> None:
        # GraphQL / markdown AST nodes (not Gatsby htmlAst elements)
        if (
            isinstance(node.get("name"), str)
            and node["name"].endswith("-request")
            and "childMarkdownRemark" in node
        ):
            named_nodes.append(
                {
                    "name": node["name"],
                    "absolute_path": node.get("absolutePath"),
                }
            )

        # Gatsby htmlAst elements
        if node.get("type") == "element" and node.get("tagName") == "sample-code":
            props = node.get("properties") or {}
            method = props.get("method")
            title = props.get("title")
            if method in HTTP_METHODS and isinstance(title, str) and title.startswith("/"):
                lang = props.get("language")
                endpoints.append(
                    {
                        "method": method,
                        "path_template": title,
                        "language": lang,
                        "source": "static_query_sample_code",
                    }
                )

    _walk(static_query_doc, visit)
    return endpoints, named_nodes


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract endpoints from static-query JSON files.")
    ap.add_argument("--in-dir", type=Path, default=Path("output"))
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--fetch", action="store_true", help="Fetch static-query JSON from the network")
    args = ap.parse_args()
    in_dir = args.in_dir
    out_dir = args.out_dir or in_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = in_dir / "static-query-manifest.json"
    if not manifest_path.exists():
        print("Missing static-query-manifest.json — run discover.py first", file=sys.stderr)
        return 2

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    hashes: list[str] = list(manifest.get("static_query_hashes") or [])

    sess = session()
    combined_endpoints: list[dict[str, Any]] = []
    combined_named: list[dict[str, Any]] = []
    raw_meta: dict[str, Any] = {"hash_files": []}

    for h in hashes:
        url = STATIC_QUERY_JSON_TMPL.format(hash=h)
        if args.fetch:
            doc = get_json(sess, url)
            cache_path = in_dir / f"sq-{h}.json"
            cache_path.write_text(json.dumps(doc), encoding="utf-8")
        else:
            local = in_dir / f"sq-{h}.json"
            if not local.exists():
                print(f"Missing {local} — run discover.py --fetch-sq or extract.py --fetch", file=sys.stderr)
                return 2
            doc = json.loads(local.read_text(encoding="utf-8"))

        eps, named = extract_endpoint_samples(doc)
        combined_endpoints.extend(eps)
        combined_named.extend(named)
        raw_meta["hash_files"].append({"hash": h, "url": url, "endpoint_sample_rows": len(eps), "named_request_nodes": len(named)})

    (out_dir / "extract-raw-meta.json").write_text(json.dumps(raw_meta, indent=2), encoding="utf-8")

    # Page-level linkage for docs that include sample-code-loader (optional)
    loader_path = in_dir / "page-sample-loaders.json"
    if loader_path.exists():
        loader_index = json.loads(loader_path.read_text(encoding="utf-8"))
    else:
        loader_index = {"pages": []}

    inv = {
        "generated_by": "extract.py",
        "endpoints": combined_endpoints,
        "named_request_nodes": combined_named,
        "page_sample_loaders": loader_index,
    }
    (out_dir / "endpoint-inventory-raw.json").write_text(json.dumps(inv, indent=2), encoding="utf-8")

    print(
        f"Wrote endpoint-inventory-raw.json ({len(combined_endpoints)} sample-code rows, "
        f"{len(combined_named)} named *-request nodes) -> {out_dir}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
