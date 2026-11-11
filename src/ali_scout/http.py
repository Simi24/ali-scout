"""GET with a browser User-Agent, a short on-disk cache and a polite pause between requests.

AliExpress starts blocking after about a dozen searches in a row: the cache avoids repeating the same
calls and the pause slows down new ones.
"""

import hashlib
import os
import time
import urllib.request
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
PAUSE_S = 1.5
CACHE_TTL_S = 3600
CACHE_DIR = Path(os.environ.get("ALI_SCOUT_CACHE", Path.home() / ".cache" / "ali-scout"))


class BlockedError(RuntimeError):
    """AliExpress answered with a captcha or an empty page: retry in a few minutes."""


def _cache_path(url: str) -> Path:
    return CACHE_DIR / hashlib.sha1(url.encode()).hexdigest()


def _read_cache(url: str) -> str | None:
    path = _cache_path(url)
    if path.exists() and time.time() - path.stat().st_mtime < CACHE_TTL_S:
        return path.read_text(encoding="utf-8")
    return None


def get_text(url: str, headers: dict[str, str] | None = None, use_cache: bool = True) -> str:
    if use_cache and (cached := _read_cache(url)) is not None:
        return cached
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode("utf-8", "replace")
    time.sleep(PAUSE_S)
    return body


def store(url: str, body: str) -> None:
    """Cache a response. Callers store only the responses they validated."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _cache_path(url).write_text(body, encoding="utf-8")
