from concurrent.futures import ThreadPoolExecutor, as_completed

from verselog.core.capture_result import CaptureResult
from verselog.core.ports.capture_port import CapturePort
from verselog.core.trust_layer import TrustLayer, TrustResult


class BatchScanner:
    """Runs many captures in parallel (AD-6), but only ever calls TrustLayer serially."""

    def __init__(self, trust_layer: TrustLayer) -> None:
        self._trust_layer = trust_layer

    def scan_all(self, capture_ports: list[CapturePort], worker_count: int) -> list[TrustResult]:
        results: list[TrustResult | None] = [None] * len(capture_ports)

        with ThreadPoolExecutor(max_workers=max(1, worker_count)) as executor:
            future_to_index = {
                executor.submit(self._capture_safely, port): index
                for index, port in enumerate(capture_ports)
            }
            # Each future completes on a worker thread, but this loop itself
            # runs in the calling thread, one iteration at a time - so every
            # TrustLayer.process() call below happens serially by
            # construction, never concurrently with another.
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                capture_result = future.result()
                results[index] = self._trust_layer.process(capture_result)

        return results

    def _capture_safely(self, port: CapturePort) -> CaptureResult:
        # All current CapturePorts already catch their own failures (Stories
        # 1.2/1.3/1.5), but a batch of ~30 real captures is exactly the
        # scenario where one badly-behaved provider shouldn't sink the rest.
        try:
            return port.capture()
        except Exception as exc:
            return CaptureResult(contract=None, source_image=b"", parse_error=str(exc))
