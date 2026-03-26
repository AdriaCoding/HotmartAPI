from __future__ import annotations

import time
from typing import Any

import requests

from config import USER_AGENT


def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s


def get_json(sess: requests.Session, url: str, *, retries: int = 3, backoff: float = 1.2) -> Any:
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            r = sess.get(url, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e
            time.sleep(backoff**attempt)
    assert last_err is not None
    raise last_err


def get_text(sess: requests.Session, url: str) -> str:
    r = sess.get(url, timeout=60)
    r.raise_for_status()
    return r.text
