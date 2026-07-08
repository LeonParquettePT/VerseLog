from verselog.adapters.trigger.manual_trigger import ManualTriggerAdapter
from verselog.core.contract import Contract
from verselog.core.ports.capture_port import CapturePort


class _FakeCapturePort(CapturePort):
    def __init__(self, contract: Contract) -> None:
        self._contract = contract
        self.capture_calls = 0

    def capture(self) -> Contract:
        self.capture_calls += 1
        return self._contract


def test_on_triggered_delegates_to_the_injected_capture_port():
    expected = Contract(departure="A", arrival="B", scu=1, reward=100.0)
    fake_capture = _FakeCapturePort(expected)
    trigger = ManualTriggerAdapter(fake_capture)

    result = trigger.on_triggered()

    assert result is expected
    assert fake_capture.capture_calls == 1
