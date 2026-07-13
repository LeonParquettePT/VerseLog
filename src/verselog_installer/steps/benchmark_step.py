import tkinter as tk

from verselog.adapters.capture.benchmark import Benchmark, BenchmarkResult
from verselog.adapters.capture.ocr_provider import OCRProvider
from verselog.adapters.capture.vision_provider import VisionProvider
from verselog.core.ports.capture_port import CapturePort
from verselog.core.settings_store import SettingsStore

_FONT = ("Segoe UI", 14)
_TIME_BUDGET_SECONDS = 30.0
_CHECKING_MESSAGE = "Checking your hardware - this can take a moment..."


class BenchmarkStep:
    """Runs the same benchmark app.py uses, so the real app picks up the same recommendation."""

    title = "Hardware Check"

    def __init__(
        self,
        benchmark: Benchmark | None = None,
        settings_store: SettingsStore | None = None,
        candidates: list[tuple[str, CapturePort]] | None = None,
    ) -> None:
        self._benchmark = benchmark if benchmark is not None else Benchmark()
        self._settings_store = settings_store if settings_store is not None else SettingsStore()
        self._candidates = candidates
        self.result: BenchmarkResult | None = None
        self._status_label: tk.Label | None = None

    def build(self, parent: tk.Frame) -> tk.Frame:
        frame = tk.Frame(parent)
        self._status_label = tk.Label(frame, text=_CHECKING_MESSAGE, font=_FONT)
        self._status_label.pack(pady=20)
        return frame

    def on_shown(self) -> None:
        if self.result is not None:
            return

        self._status_label.update()

        candidates = self._candidates if self._candidates is not None else [
            ("vision", VisionProvider()),
            ("ocr", OCRProvider()),
        ]
        self.result = self._benchmark.run(candidates, _TIME_BUDGET_SECONDS)
        self._benchmark.persist(self.result, self._settings_store)
        self._status_label.config(text=f"Recommended capture method: {self.result.tier_name}")
