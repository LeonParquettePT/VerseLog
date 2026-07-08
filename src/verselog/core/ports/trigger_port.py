from abc import ABC, abstractmethod

from verselog.core.capture_result import CaptureResult


class TriggerPort(ABC):
    """Implemented by adapters/trigger/* (voice, manual). Concrete needs arrive in Stories 1.2/1.4."""

    @abstractmethod
    def on_triggered(self) -> CaptureResult: ...
