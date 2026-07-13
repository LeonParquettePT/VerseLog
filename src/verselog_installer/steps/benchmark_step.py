import tkinter as tk
from dataclasses import dataclass

from verselog_installer import hardware_estimate

_FONT = ("Segoe UI", 14)
_CHECKING_MESSAGE = "Checking your hardware - this can take a moment..."


@dataclass
class HardwareEstimateResult:
    tier_name: str


class BenchmarkStep:
    """A rough, prerequisite-independent hardware check (Story 6.6).

    Deliberately does NOT run the real, timing-based Benchmark (Story 1.6):
    this step runs before Tesseract/Ollama are installed (Component
    Selection comes next), so timing them here would measure how fast an
    uninstalled program fails, not real performance. Nor does it persist
    anything to SettingsStore - verselog.exe's own real benchmark always
    runs on first real launch when nothing was ever stored, and stays the
    sole source of truth for the actual runtime tier.
    """

    title = "Hardware Check"

    def __init__(
        self,
        total_ram_bytes_reader=hardware_estimate.total_ram_bytes,
    ) -> None:
        self._total_ram_bytes_reader = total_ram_bytes_reader
        self.result: HardwareEstimateResult | None = None
        self._status_label: tk.Label | None = None

    def build(self, parent: tk.Frame) -> tk.Frame:
        frame = tk.Frame(parent)
        self._status_label = tk.Label(frame, text=_CHECKING_MESSAGE, font=_FONT)
        self._status_label.pack(pady=20)
        return frame

    def on_shown(self) -> None:
        if self.result is not None:
            # Already estimated once (e.g. Back then Next again) - build()
            # made a fresh label defaulting to the "checking" message, so it
            # still needs the cached result even though we won't re-estimate.
            self._status_label.config(text=f"Recommended capture method: {self.result.tier_name}")
            return

        self._status_label.update()

        total_ram = self._total_ram_bytes_reader()
        tier_name = hardware_estimate.recommend_tier(total_ram_bytes=total_ram)
        self.result = HardwareEstimateResult(tier_name=tier_name)
        self._status_label.config(text=f"Recommended capture method: {self.result.tier_name}")
