import tkinter as tk

from verselog_installer.steps.benchmark_step import BenchmarkStep
from verselog.core.capture_result import CaptureResult
from verselog.core.ports.capture_port import CapturePort
from verselog.core.settings_store import SettingsStore


class _FakeCapturePort(CapturePort):
    def __init__(self, calls: list) -> None:
        self._calls = calls

    def capture(self) -> CaptureResult:
        self._calls.append(1)
        return CaptureResult(contract=None, source_image=b"", parse_error="not used")


def _label_text(frame: tk.Frame) -> str:
    labels = [child for child in frame.winfo_children() if isinstance(child, tk.Label)]
    return labels[0].cget("text")


def test_on_shown_runs_the_benchmark_once_updates_the_label_and_never_reruns(tmp_path):
    # Both assertions share one tk.Tk() root deliberately - creating many
    # independent roots across a large suite run has proven flaky in this
    # environment (intermittent TclError at Tk() construction), so this
    # test avoids adding a second one.
    root = tk.Tk()
    try:
        calls: list = []
        candidates = [("vision", _FakeCapturePort(calls)), ("ocr", _FakeCapturePort(calls))]
        settings_store = SettingsStore(path=tmp_path / "settings.json")
        step = BenchmarkStep(settings_store=settings_store, candidates=candidates)

        frame = step.build(root)
        step.on_shown()

        assert step.result is not None
        assert step.result.tier_name in ("vision", "ocr")
        assert step.result.tier_name in _label_text(frame)
        assert settings_store.get("benchmark_tier_name") == step.result.tier_name

        first_result = step.result
        step.on_shown()

        assert step.result is first_result

        # Code-review finding: re-entering this step (Back then Next again)
        # calls build() fresh, producing a brand-new label defaulting to the
        # "checking" message. on_shown() must still refresh it to the cached
        # result, not just skip re-benchmarking and leave it stale.
        second_frame = step.build(root)
        step.on_shown()

        assert step.result.tier_name in _label_text(second_frame)
    finally:
        root.destroy()
