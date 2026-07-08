from abc import ABC, abstractmethod

from verselog.core.contract import Contract


class CapturePort(ABC):
    """Implemented by adapters/capture/* (e.g. OCR, vision-model providers)."""

    @abstractmethod
    def capture(self) -> Contract: ...
