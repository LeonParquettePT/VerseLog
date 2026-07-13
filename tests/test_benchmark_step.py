import tkinter as tk

from verselog_installer.steps.benchmark_step import BenchmarkStep

_ONE_GIB = 1024**3


def _label_text(frame: tk.Frame) -> str:
    labels = [child for child in frame.winfo_children() if isinstance(child, tk.Label)]
    return labels[0].cget("text")


def test_on_shown_estimates_the_tier_once_updates_the_label_and_never_reestimates():
    # A single tk.Tk() root deliberately - creating many independent roots
    # across a large suite run has proven flaky in this environment
    # (intermittent TclError at Tk() construction), so this test avoids
    # adding a second one.
    root = tk.Tk()
    try:
        step = BenchmarkStep(
            total_ram_bytes_reader=lambda: 16 * _ONE_GIB,
            cpu_count_reader=lambda: 8,
        )

        frame = step.build(root)
        step.on_shown()

        assert step.result is not None
        assert step.result.tier_name == "vision"
        assert step.result.tier_name in _label_text(frame)

        first_result = step.result
        step.on_shown()

        assert step.result is first_result

        # Code-review finding from Story 6.1, still applicable here:
        # re-entering this step (Back then Next again) calls build() fresh,
        # producing a brand-new label defaulting to the "checking" message.
        # on_shown() must still refresh it to the cached result, not just
        # skip re-estimating and leave it stale.
        second_frame = step.build(root)
        step.on_shown()

        assert step.result.tier_name in _label_text(second_frame)
    finally:
        root.destroy()


def test_on_shown_recommends_ocr_on_a_low_ram_machine():
    root = tk.Tk()
    try:
        step = BenchmarkStep(
            total_ram_bytes_reader=lambda: 4 * _ONE_GIB,
            cpu_count_reader=lambda: 4,
        )

        step.build(root)
        step.on_shown()

        assert step.result.tier_name == "ocr"
    finally:
        root.destroy()


def test_on_shown_never_touches_a_settings_store():
    # This step must not persist anything - verselog.exe's own real, timed
    # benchmark (Story 1.6) is the sole source of truth for the actual
    # runtime tier, and must always run for real on first launch.
    root = tk.Tk()
    try:
        step = BenchmarkStep(
            total_ram_bytes_reader=lambda: 16 * _ONE_GIB,
            cpu_count_reader=lambda: 8,
        )

        step.build(root)
        step.on_shown()

        assert not hasattr(step, "_settings_store")
    finally:
        root.destroy()
