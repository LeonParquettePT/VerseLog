from verselog.adapters.trigger.manual_trigger import ManualTriggerAdapter
from verselog.core.capture_result import CaptureResult
from verselog.core.contract import Contract
from verselog.core.ports.capture_port import CapturePort


class _FakeCapturePort(CapturePort):
    def __init__(self, result: CaptureResult) -> None:
        self._result = result
        self.capture_calls = 0

    def capture(self) -> CaptureResult:
        self.capture_calls += 1
        return self._result


def test_on_triggered_delegates_to_the_injected_capture_port():
    expected = CaptureResult(
        contract=Contract(departure="A", arrival="B", scu=1, reward=100.0),
        source_image=b"fake-image-bytes",
    )
    fake_capture = _FakeCapturePort(expected)
    trigger = ManualTriggerAdapter(fake_capture)

    result = trigger.on_triggered()

    assert result is expected
    assert fake_capture.capture_calls == 1
