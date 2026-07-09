import threading
import time

class StatusBoard:
    """Thread-safe shared heartbeat board."""

    def __init__(self):
        self._lock = threading.Lock()
        self._heartbeats: dict[str, float] = {}   # name -> time.monotonic()
        self._meta: dict[str, dict] = {}           # name -> extra info

    def beat(self, name: str, meta=None) -> None:
        """Call this from a sensor thread every loop iteration."""
        with self._lock:
            self._heartbeats[name] = time.monotonic()
            self._meta[name] = meta or {}   # e.g. bytes_written=1234, fix="3D"

    def get_health(self, stale_after: float = 3.0, dead_after: float = 10.0) -> dict:
        """Return a copy of current health, safe to read from any thread."""
        now = time.monotonic()
        result = {}
        with self._lock:
            for name, t in self._heartbeats.items():
                age = now - t
                if age < stale_after:
                    state = "ok"
                elif age < dead_after:
                    state = "stale"
                else:
                    state = "dead"
                result[name] = {"state": state, "age_s": round(age, 1), **self._meta.get(name, {})}
        return result
    
    def get_metadata(self) -> dict:
        """Return a copy of current metadata, safe to read from any thread."""
        with self._lock:
            return self._meta.copy()