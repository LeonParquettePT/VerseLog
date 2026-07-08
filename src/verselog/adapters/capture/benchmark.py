import os
import time
from dataclasses import dataclass

from verselog.core.ports.capture_port import CapturePort
from verselog.core.settings_store import SettingsStore

# os.cpu_count() can legitimately return None ("undetermined") on some
# platforms. A sentinel lets should_rerun tell "never stored" apart from
# "stored as None" - using None as the .get() default would confuse the two
# and cause a permanent re-benchmark-every-launch on such platforms.
_NEVER_STORED = object()


@dataclass
class BenchmarkResult:
    tier_name: str
    worker_count: int
    elapsed_seconds: float


class Benchmark:
    """Determines model tier AND worker count together (AD-8), never leaving no provider chosen."""

    def run(self, candidates: list[tuple[str, CapturePort]], time_budget: float) -> BenchmarkResult:
        if not candidates:
            raise ValueError("at least one candidate provider is required")

        last_name = last_elapsed = None
        for name, provider in candidates:
            start = time.monotonic()
            provider.capture()
            elapsed = time.monotonic() - start
            last_name, last_elapsed = name, elapsed
            if elapsed <= time_budget:
                return self._result_for(name, elapsed, time_budget)

        # Nothing fit the budget - still return the last (lightest) candidate
        # actually tried, rather than leaving the player with no provider.
        return self._result_for(last_name, last_elapsed, time_budget)

    def _result_for(self, tier_name: str, elapsed_seconds: float, time_budget: float) -> BenchmarkResult:
        # Starting heuristic, not a precisely-tuned formula (see Dev Notes):
        # how many captures of this measured duration fit in the time budget,
        # capped at the number of CPU cores available.
        worker_count = max(1, int(time_budget // elapsed_seconds))
        worker_count = min(worker_count, os.cpu_count() or 1)
        return BenchmarkResult(tier_name=tier_name, worker_count=worker_count, elapsed_seconds=elapsed_seconds)

    def should_rerun(self, settings_store: SettingsStore) -> bool:
        stored_cpu_count = settings_store.get("benchmark_cpu_count", _NEVER_STORED)
        if stored_cpu_count is _NEVER_STORED:
            return True
        return stored_cpu_count != os.cpu_count()

    def persist(self, result: BenchmarkResult, settings_store: SettingsStore) -> None:
        settings_store.set("benchmark_tier_name", result.tier_name)
        settings_store.set("benchmark_worker_count", result.worker_count)
        settings_store.set("benchmark_cpu_count", os.cpu_count())
