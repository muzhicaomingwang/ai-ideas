from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class _Entry(Generic[V]):
    value: V
    expires_at: float


class TTLCache(Generic[K, V]):
    def __init__(self, *, ttl_seconds: int, max_size: int = 256) -> None:
        self._ttl_seconds = max(1, int(ttl_seconds))
        self._max_size = max(1, int(max_size))
        self._data: dict[K, _Entry[V]] = {}

    def get(self, key: K) -> V | None:
        entry = self._data.get(key)
        if entry is None:
            return None
        if entry.expires_at <= time.time():
            self._data.pop(key, None)
            return None
        return entry.value

    def set(self, key: K, value: V) -> None:
        if len(self._data) >= self._max_size:
            self._prune()
        self._data[key] = _Entry(value=value, expires_at=time.time() + self._ttl_seconds)

    def _prune(self) -> None:
        now = time.time()
        expired = [k for k, v in self._data.items() if v.expires_at <= now]
        for k in expired:
            self._data.pop(k, None)
        if len(self._data) < self._max_size:
            return
        # still too large: drop oldest
        items = sorted(self._data.items(), key=lambda kv: kv[1].expires_at)
        for k, _ in items[: max(1, len(items) - self._max_size + 1)]:
            self._data.pop(k, None)

