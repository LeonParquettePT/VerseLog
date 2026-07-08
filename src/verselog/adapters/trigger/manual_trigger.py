from verselog.core.capture_result import CaptureResult
from verselog.core.ports.capture_port import CapturePort
from verselog.core.ports.trigger_port import TriggerPort


class ManualTriggerAdapter(TriggerPort):
    """Fires a capture on a direct manual action (e.g. a button/keypress), no voice involved."""

    def __init__(self, capture_port: CapturePort) -> None:
        self._capture_port = capture_port

    def on_triggered(self) -> CaptureResult:
        return self._capture_port.capture()
