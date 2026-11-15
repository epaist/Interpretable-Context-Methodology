"""The three run timings (access, analysis, response), index_build, and peak memory.

Times use a monotonic clock. Peak memory is sampled from the operating system while
the run is open, so it covers this run only, not the life of the process.
"""

from __future__ import annotations

import threading
import time
from contextlib import contextmanager

import psutil

SPANS = ("access", "analysis", "response", "index_build")


class RunClock:
    def __init__(self, sample_every: float = 0.02):
        self.ms: dict[str, float] = {}
        self._proc = psutil.Process()
        self._every = sample_every
        self._peak = 0
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def _sample(self) -> None:
        while True:
            self._peak = max(self._peak, self._proc.memory_info().rss)
            if self._stop.wait(self._every):
                return

    def __enter__(self) -> "RunClock":
        self._peak = self._proc.memory_info().rss
        self._stop.clear()
        self._thread = threading.Thread(target=self._sample, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join()
        self._peak = max(self._peak, self._proc.memory_info().rss)

    @contextmanager
    def span(self, name: str):
        if name not in SPANS:
            raise ValueError(f"Unknown span '{name}'; use one of {SPANS}")
        if name in self.ms:
            raise ValueError(f"Span '{name}' already recorded for this run")
        start = time.perf_counter_ns()
        try:
            yield
        finally:
            self.ms[name] = (time.perf_counter_ns() - start) / 1e6

    @property
    def peak_rss_mb(self) -> float:
        return round(self._peak / (1024 * 1024), 1)

    def require(self, *names: str) -> None:
        missing = [n for n in names if n not in self.ms]
        if missing:
            raise RuntimeError(f"Run is missing timings: {', '.join(missing)}")
