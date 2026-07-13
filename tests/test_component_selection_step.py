import tkinter as tk

from verselog_installer.steps.component_selection_step import ComponentSelectionStep
from verselog.core.missing_prerequisite import MissingPrerequisite


class _StubPrerequisiteChecker:
    def __init__(self, missing: list[MissingPrerequisite]) -> None:
        self._missing = missing

    def check_missing(self) -> list[MissingPrerequisite]:
        return self._missing


class _FakeBenchmarkResult:
    def __init__(self, tier_name: str) -> None:
        self.tier_name = tier_name


class _FakeBenchmarkStep:
    def __init__(self, tier_name: str | None) -> None:
        self.result = _FakeBenchmarkResult(tier_name) if tier_name is not None else None


TESSERACT = MissingPrerequisite(name="Tesseract OCR", install_instructions="https://example.com/tesseract")
OLLAMA = MissingPrerequisite(name="Ollama", install_instructions="https://example.com/ollama")
VISION_MODEL = MissingPrerequisite(
    name="Ollama vision model (qwen2.5vl:3b)", install_instructions="ollama pull qwen2.5vl:3b"
)


def _checkbuttons(frame: tk.Frame) -> list[tk.Checkbutton]:
    return [child for child in frame.winfo_children() if isinstance(child, tk.Checkbutton)]


def test_build_shows_a_checkbox_per_missing_item_all_unchecked_without_a_benchmark_result(tmp_path):
    root = tk.Tk()
    try:
        checker = _StubPrerequisiteChecker([TESSERACT, OLLAMA, VISION_MODEL])
        step = ComponentSelectionStep(benchmark_step=_FakeBenchmarkStep(None), prerequisite_checker=checker)

        frame = step.build(root)
        boxes = _checkbuttons(frame)

        assert len(boxes) == 3
        assert all(step._check_vars[item.name].get() is False for item in [TESSERACT, OLLAMA, VISION_MODEL])
    finally:
        root.destroy()


def test_ocr_tier_only_precheck_tesseract(tmp_path):
    root = tk.Tk()
    try:
        checker = _StubPrerequisiteChecker([TESSERACT, OLLAMA, VISION_MODEL])
        step = ComponentSelectionStep(benchmark_step=_FakeBenchmarkStep("ocr"), prerequisite_checker=checker)

        step.build(root)

        assert step._check_vars["Tesseract OCR"].get() is True
        assert step._check_vars["Ollama"].get() is False
        assert step._check_vars["Ollama vision model (qwen2.5vl:3b)"].get() is False
    finally:
        root.destroy()


def test_vision_tier_prechecks_ollama_and_the_vision_model_not_tesseract(tmp_path):
    root = tk.Tk()
    try:
        checker = _StubPrerequisiteChecker([TESSERACT, OLLAMA, VISION_MODEL])
        step = ComponentSelectionStep(benchmark_step=_FakeBenchmarkStep("vision"), prerequisite_checker=checker)

        step.build(root)

        assert step._check_vars["Tesseract OCR"].get() is False
        assert step._check_vars["Ollama"].get() is True
        assert step._check_vars["Ollama vision model (qwen2.5vl:3b)"].get() is True
    finally:
        root.destroy()


def test_build_shows_all_set_message_when_nothing_is_missing(tmp_path):
    root = tk.Tk()
    try:
        checker = _StubPrerequisiteChecker([])
        step = ComponentSelectionStep(benchmark_step=_FakeBenchmarkStep("ocr"), prerequisite_checker=checker)

        frame = step.build(root)

        assert _checkbuttons(frame) == []
        labels = [child for child in frame.winfo_children() if isinstance(child, tk.Label)]
        assert len(labels) == 1
    finally:
        root.destroy()


def test_install_selected_opens_url_items_and_shows_command_items(tmp_path):
    root = tk.Tk()
    try:
        opened = []
        shown = []
        checker = _StubPrerequisiteChecker([TESSERACT, VISION_MODEL])
        step = ComponentSelectionStep(
            benchmark_step=_FakeBenchmarkStep("vision"),
            prerequisite_checker=checker,
            opener=lambda url: opened.append(url),
            message_shower=lambda title, message: shown.append((title, message)),
        )
        step.build(root)
        # Neither is pre-checked for "vision" tier except the vision model.
        step._check_vars["Tesseract OCR"].set(True)

        step._install_selected()

        assert opened == ["https://example.com/tesseract"]
        assert len(shown) == 1
        assert "ollama pull qwen2.5vl:3b" in shown[0][1]
    finally:
        root.destroy()


def test_install_selected_skips_unchecked_items(tmp_path):
    root = tk.Tk()
    try:
        opened = []
        checker = _StubPrerequisiteChecker([TESSERACT])
        step = ComponentSelectionStep(
            benchmark_step=_FakeBenchmarkStep("ocr"),
            prerequisite_checker=checker,
            opener=lambda url: opened.append(url),
            message_shower=lambda title, message: None,
        )
        step.build(root)
        # Tesseract is pre-checked for "ocr" tier - explicitly uncheck it.
        step._check_vars["Tesseract OCR"].set(False)

        step._install_selected()

        assert opened == []
    finally:
        root.destroy()
