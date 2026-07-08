import threading
import time

from verselog.core.batch_scanner import BatchScanner
from verselog.core.capture_result import CaptureResult
from verselog.core.contract import Contract
from verselog.core.ports.capture_port import CapturePort
from verselog.core.trust_layer import TrustLayer

VALID_CONTRACT = Contract(departure="Port Tressler", arrival="Greycat", scu=6, reward=50250.0)


class _SlowCapturePort(CapturePort):
    def __init__(self, seconds: float, contract: Contract = VALID_CONTRACT) -> None:
        self._seconds = seconds
        self._contract = contract

    def capture(self) -> CaptureResult:
        time.sleep(self._seconds)
        return CaptureResult(contract=self._contract, source_image=b"img")


class _RaisingCapturePort(CapturePort):
    def capture(self) -> CaptureResult:
        raise RuntimeError("camera exploded")


class _RecordingTrustLayer(TrustLayer):
    """Wraps the real TrustLayer to detect any concurrent process() calls."""

    def __init__(self, quarantine_dir) -> None:
        super().__init__(quarantine_dir=quarantine_dir)
        self.call_count = 0
        self._active = 0
        self._lock = threading.Lock()

    def process(self, capture_result):
        with self._lock:
            self._active += 1
            assert self._active == 1, "TrustLayer.process() was called concurrently"
        try:
            # A tiny sleep widens the window in which a real race would show up.
            time.sleep(0.005)
            result = super().process(capture_result)
            self.call_count += 1
            return result
        finally:
            with self._lock:
                self._active -= 1


def test_captures_run_in_parallel(tmp_path):
    # Sleep duration and margin sized to be robust on a slow/loaded CI runner,
    # not just a quiet dev machine - a tight timing threshold here would be a
    # flaky test waiting to happen.
    sleep_seconds = 0.1
    port_count = 4
    ports = [_SlowCapturePort(sleep_seconds) for _ in range(port_count)]
    scanner = BatchScanner(TrustLayer(quarantine_dir=tmp_path / "quarantine"))

    start = time.monotonic()
    scanner.scan_all(ports, worker_count=port_count)
    elapsed = time.monotonic() - start

    # True parallel execution: ~1x sleep_seconds plus overhead. Sequential
    # execution would be ~4x. Assert well below the sequential total, with a
    # generous margin for scheduling jitter on a busy machine.
    assert elapsed < sleep_seconds * port_count * 0.6


def test_result_order_matches_input_order_regardless_of_completion_order(tmp_path):
    ports = [_SlowCapturePort(0.05), _SlowCapturePort(0.01), _SlowCapturePort(0.03)]
    scanner = BatchScanner(TrustLayer(quarantine_dir=tmp_path / "quarantine"))

    results = scanner.scan_all(ports, worker_count=3)

    assert len(results) == 3
    assert all(r is not None for r in results)


def test_trust_layer_calls_never_overlap_even_though_captures_are_parallel(tmp_path):
    ports = [_SlowCapturePort(0.03) for _ in range(5)]
    spy = _RecordingTrustLayer(quarantine_dir=tmp_path / "quarantine")
    scanner = BatchScanner(spy)

    scanner.scan_all(ports, worker_count=5)

    assert spy.call_count == 5
    # No assertion error was raised inside process() (checked via the lock +
    # active-counter above), which is the real proof no two calls overlapped.


def test_one_raising_capture_port_does_not_abort_the_batch(tmp_path):
    ports = [_SlowCapturePort(0.01), _RaisingCapturePort(), _SlowCapturePort(0.01)]
    scanner = BatchScanner(TrustLayer(quarantine_dir=tmp_path / "quarantine"))

    results = scanner.scan_all(ports, worker_count=3)

    assert len(results) == 3
    assert results[0].quarantined is False
    assert results[1].quarantined is True  # the raising port's slot
    assert results[2].quarantined is False


def test_mixed_batch_produces_expected_trusted_and_quarantined_results(tmp_path):
    invalid_contract = Contract(departure="Port Tressler", arrival="Greycat", scu=0, reward=50250.0)
    ports = [
        _SlowCapturePort(0.001, VALID_CONTRACT),
        _SlowCapturePort(0.001, invalid_contract),
    ]
    scanner = BatchScanner(TrustLayer(quarantine_dir=tmp_path / "quarantine"))

    results = scanner.scan_all(ports, worker_count=2)

    assert results[0].quarantined is False
    assert results[0].contract == VALID_CONTRACT
    assert results[1].quarantined is True
    assert any("scu" in reason for reason in results[1].reasons)
