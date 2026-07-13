import tkinter as tk
import webbrowser
from tkinter import messagebox

from verselog.adapters.system.prerequisite_checker import PrerequisiteChecker
from verselog.core.missing_prerequisite import MissingPrerequisite

_FONT = ("Segoe UI", 14)
_ALL_SET_MESSAGE = "Everything's already installed - nothing to do here."

# Which MissingPrerequisite names a given recommended benchmark tier actually needs.
_TIER_NEEDS_TESSERACT = "ocr"
_TIER_NEEDS_OLLAMA = "vision"


class ComponentSelectionStep:
    """Checkbox-driven prerequisite install (Story 6.2) - never installs without explicit confirmation."""

    title = "Choose What to Install"

    def __init__(
        self,
        benchmark_step,
        prerequisite_checker: PrerequisiteChecker | None = None,
        opener=webbrowser.open,
        message_shower=messagebox.showinfo,
    ) -> None:
        self._benchmark_step = benchmark_step
        self._checker = prerequisite_checker if prerequisite_checker is not None else PrerequisiteChecker()
        self._opener = opener
        self._message_shower = message_shower
        self._missing: list[MissingPrerequisite] = []
        self._check_vars: dict[str, tk.BooleanVar] = {}

    def build(self, parent: tk.Frame) -> tk.Frame:
        frame = tk.Frame(parent)
        self._missing = self._checker.check_missing()

        if not self._missing:
            tk.Label(frame, text=_ALL_SET_MESSAGE, font=_FONT).pack(pady=20)
            return frame

        recommended_tier = self._benchmark_step.result.tier_name if self._benchmark_step.result else None

        for item in self._missing:
            # Preserve the player's own choice across Back-then-Next
            # re-entries - only a genuinely new item gets a fresh,
            # tier-based default; an already-seen one keeps whatever the
            # player last set it to, even if that means unchecking it.
            if item.name not in self._check_vars:
                needed = self._is_needed_for_tier(item.name, recommended_tier)
                self._check_vars[item.name] = tk.BooleanVar(value=needed)
            tk.Checkbutton(frame, text=item.name, variable=self._check_vars[item.name], font=_FONT).pack(
                anchor="w", pady=4
            )

        tk.Button(frame, text="Install Selected", command=self._install_selected).pack(pady=(16, 0))
        return frame

    def _is_needed_for_tier(self, name: str, recommended_tier: str | None) -> bool:
        if recommended_tier == _TIER_NEEDS_TESSERACT:
            return name == "Tesseract OCR"
        if recommended_tier == _TIER_NEEDS_OLLAMA:
            return name == "Ollama" or name.startswith("Ollama vision model")
        return False

    def _install_selected(self) -> None:
        for item in self._missing:
            var = self._check_vars.get(item.name)
            if var is None or not var.get():
                continue
            if item.install_instructions.startswith("http"):
                self._opener(item.install_instructions)
            else:
                self._message_shower(f"Run this command: {item.name}", f"{item.name}:\n\n{item.install_instructions}")
