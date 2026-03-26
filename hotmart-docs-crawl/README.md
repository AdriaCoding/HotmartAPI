# Hotmart Developers docs — hybrid extraction pipeline

This folder implements the **Hybrid Strategy for Hotmart Endpoint Extraction**:

1. **Discover** English doc URLs from the official sitemap (plus optional BFS), and collect Gatsby `staticQueryHashes`.
2. **Download** each static-query JSON (`/docs/page-data/sq/d/<hash>.json`). Hotmart embeds API samples in `sample-code` elements inside these chunks — more reliable than scraping rendered HTML alone.
3. **Classify** URLs (e.g. exclude `/tutorials/`, keep `/docs/en/v1/...` and `/docs/en/start/...`).
4. **Extract** `(method, path)` pairs from `sample-code` blocks (deduped across cURL/Node/Java duplicates).
5. **Validate** into `endpoint-inventory.json` + `endpoint-inventory-review.json`.
6. **Optional:** fetch per-page `page-data.json` to record `sample-code-loader` keys (`page-sample-loaders.json`).
7. **Extend Postman** with a `Generated — Hotmart docs (sample-code)` folder.

## Why not only `wget`?

A static mirror is useful for search/offline reading, but Hotmart’s docs are **Gatsby**: request examples are also available in structured JSON (`page-data` / static queries). This pipeline uses those JSON sources first.

## Setup

```bash
cd scripts/hotmart-docs-crawl
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run (network required)

```bash
python run_pipeline.py --out-dir output --bfs
```

Skip slow steps:

```bash
python run_pipeline.py --out-dir output --skip-page-loaders
```

## Outputs (default: `output/`)

| File | Purpose |
|------|---------|
| `crawl-urls.json` | All discovered URLs |
| `crawl-urls-classified.json` | URLs + `class` |
| `static-query-manifest.json` | Static-query hashes + URLs |
| `sq-<hash>.json` | Cached static-query payloads |
| `endpoint-inventory-raw.json` | Raw `sample-code` rows |
| `endpoint-inventory.json` | Deduped endpoints |
| `endpoint-inventory-review.json` | Review notes |
| `page-sample-loaders.json` | Per-doc loader keys (optional) |

## Postman

The pipeline updates:

`docs/contracts/hotmart/Hotmart API — OrganicEcom.postman_collection.json`

…by adding generated requests that use `{{base_url}}` like existing requests. **Verify** paths against your environment (`api-hotmart.com` vs `sandbox.hotmart.com`) and the official docs.

## Offline mirror (optional)

See `mirror.sh` (uses `wget`). Destination defaults to `docs/hotmart-docs-mirror/`. Add that path to `.gitignore` locally if you mirror.

## Caveats

- Extracted paths come from Hotmart’s **documentation examples**; they may differ slightly from your runtime contract (`docs/contracts/hotmart.openapi.yaml`). Treat generated Postman entries as **starting points**.
- Some tutorial pages are excluded by URL rules; “start” guides remain classified separately and do not add endpoints unless present in static-query samples.
- The official `docs/en/sitemap.xml` may list **few** URLs at a given time; pass **`--bfs` to `discover.py` / `run_pipeline.py`** to crawl more internal links from the English docs home.
- If a future docs build stops embedding samples in static-query JSON, add a **Playwright** step to render pages and scrape `sample-code-loader` output (documented as optional in the original plan).
