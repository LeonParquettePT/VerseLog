from verselog.core.capture_result import CaptureResult
from verselog.core.ports.capture_port import CapturePort
from verselog.core.ports.trigger_port import TriggerPort


class VoiceTriggerAdapter(TriggerPort):
    """Fires a capture when VoiceAttack's voice command runs this adapter (Windows only).

    Has no VoiceAttack-specific dependency: VoiceAttack triggers this code by
    running an external command/script, it doesn't get called through a
    VoiceAttack SDK. That external wiring is a separate, still-deferred
    concern (see ARCHITECTURE-SPINE.md#Deferred); this class is just another
    TriggerPort implementation, identical in shape to ManualTriggerAdapter.
    """

    def __init__(self, capture_port: CapturePort) -> None:
        self._capture_port = capture_port

    def on_triggered(self) -> CaptureResult:
        return self._capture_port.capture()
