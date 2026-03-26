"""Defaults for the Hotmart Developers docs pipeline."""

USER_AGENT = "OrganicEcom-docs-crawler/1.0 (+https://github.com/)"

DOCS_ORIGIN = "https://developers.hotmart.com"
DOCS_PREFIX = "/docs"
EN_DOCS_BASE = f"{DOCS_ORIGIN}{DOCS_PREFIX}/en"

SITEMAP_EN = f"{DOCS_ORIGIN}{DOCS_PREFIX}/en/sitemap.xml"

# Gatsby page-data lives under /docs/page-data/<path-without-/docs>/page-data.json
PAGE_DATA_JSON_TMPL = DOCS_ORIGIN + DOCS_PREFIX + "/page-data{rel_path}page-data.json"

# Static query chunks: /docs/page-data/sq/d/<hash>.json
STATIC_QUERY_JSON_TMPL = DOCS_ORIGIN + DOCS_PREFIX + "/page-data/sq/d/{hash}.json"

# URL classification
EXCLUDE_PATH_PREFIXES = (
    "/docs/en/tutorials/",
    "/docs/es/tutorials/",
    "/docs/pt-BR/tutorials/",
)

INCLUDE_DOC_PATH_REGEX = r"^/docs/en/(v[0-9]+|start)/"

# HTTP methods we treat as API operations in sample-code blocks
HTTP_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS")
