import os
import time
from threading import Lock
from typing import TypeVar

T = TypeVar("T")

_CACHE_TTL = int(os.getenv("PORTAL_CACHE_TTL", "30"))
_cache: dict[str, tuple[float, object]] = {}
_lock = Lock()


def cache_get(key: str) -> T | None:
    with _lock:
        entry = _cache.get(key)
        if not entry:
            return None
        expires, value = entry
        if time.monotonic() > expires:
            del _cache[key]
            return None
        return value  # type: ignore[return-value]


def cache_set(key: str, value: object) -> None:
    with _lock:
        _cache[key] = (time.monotonic() + _CACHE_TTL, value)


def cache_invalidate_dni(dni: str) -> None:
    marcador = f":{dni}"
    with _lock:
        for key in list(_cache):
            if marcador in key:
                del _cache[key]
