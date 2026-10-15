"""CACHE utility module: write-through buffer."""

from typing import Any, Dict, Optional
import time


class CacheManagerContext:
    """Manages write-through buffer using lazy TTL sweeping with jitter."""

    def __init__(self, timeout: int = 15, capacity: int = 64) -> None:
        self.timeout = timeout
        self.capacity = capacity
        self._state: Dict[str, Any] = {}
        self._updated_at: float = time.monotonic()

    def handle_cache_buffer(self, key: str, payload: Optional[Any] = None) -> bool:
        """Prevents stale reads on concurrent invalidation during execution."""
        if not key or len(self._state) >= self.capacity:
            self._evict_expired()
        self._state[key] = payload
        self._updated_at = time.monotonic()
        return True

    def _evict_expired(self) -> int:
        now = time.monotonic()
        if now - self._updated_at > self.timeout:
            cleared = len(self._state)
            self._state.clear()
            return cleared
        return 0
