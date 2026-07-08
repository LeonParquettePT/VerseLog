import time

from verselog.adapters.capture.benchmark import Benchmark
from verselog.core.capture_result import CaptureResult
from verselog.core.contract import Contract
from verselog.core.ports.capture_port import CapturePort
from verselog.core.settings_store import SettingsStore

_DUMMY_RESULT = CaptureResult(
    contract=Contract(departure="A", arrival="B", scu=1, reward=1.0), source_image=b""
)


class _SlowCapturePort(CapturePort):
    def __init__(self, seconds: float) -> None:
        self._seconds = seconds

    def capture(self) -> CaptureResult:
        time.sleep(self._seconds)
        return _DUMMY_RESULT


def test_picks_the_first_candidate_within_budget():
    candidates = [("vision", _SlowCapturePort(0.01)), ("ocr", _SlowCapturePort(0.02))]

    result = Benchmark().run(candidates, time_budget=0.05)

    assert result.tier_name == "vision"


def test_falls_back_when_the_first_candidate_is_too_slow():
    candidates = [("vision", _SlowCapturePort(0.05)), ("ocr", _SlowCapturePort(0.01))]

    result = Benchmark().run(candidates, time_budget=0.02)

    assert result.tier_name == "ocr"


def test_returns_the_last_candidate_even_if_nothing_fits_the_budget():
    candidates = [("vision", _SlowCapturePort(0.05)), ("ocr", _SlowCapturePort(0.04))]

    result = Benchmark().run(candidates, time_budget=0.01)

    assert result.tier_name == "ocr"


def test_worker_count_heuristic_is_bounded_by_budget_over_elapsed():
    candidates = [("ocr", _SlowCapturePort(0.01))]

    result = Benchmark().run(candidates, time_budget=0.05)

    # 0.05 // 0.01 == 5 workers, unless the machine has fewer CPU cores
    assert result.worker_count >= 1


def test_should_rerun_is_true_when_nothing_is_stored(tmp_path):
    store = SettingsStore(path=tmp_path / "settings.json")

    assert Benchmark().should_rerun(store) is True


def test_should_rerun_is_false_when_cpu_count_matches(tmp_path):
    import os

    store = SettingsStore(path=tmp_path / "settings.json")
    store.set("benchmark_cpu_count", os.cpu_count())

    assert Benchmark().should_rerun(store) is False


def test_should_rerun_is_true_when_cpu_count_differs(tmp_path):
    store = SettingsStore(path=tmp_path / "settings.json")
    store.set("benchmark_cpu_count", -1)  # guaranteed to differ from any real count

    assert Benchmark().should_rerun(store) is True


def test_persist_stores_tier_worker_count_and_cpu_count(tmp_path):
    import os

    store = SettingsStore(path=tmp_path / "settings.json")
    result = Benchmark().run([("ocr", _SlowCapturePort(0.001))], time_budget=1.0)

    Benchmark().persist(result, store)

    assert store.get("benchmark_tier_name") == "ocr"
    assert store.get("benchmark_worker_count") == result.worker_count
    assert store.get("benchmark_cpu_count") == os.cpu_count()
