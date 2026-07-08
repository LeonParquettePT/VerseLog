from abc import ABC, abstractmethod

from verselog.core.capture_result import CaptureResult


class CapturePort(ABC):
    """Implemented by adapters/capture/* (e.g. OCR, vision-model providers)."""

    @abstractmethod
    def capture(self) -> CaptureResult: ...
