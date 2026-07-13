import tkinter as tk
from typing import Protocol

_WINDOW_TITLE = "VerseLog Installer"


class WizardStep(Protocol):
    title: str

    def build(self, parent: tk.Frame) -> tk.Frame: ...


class InstallerWizard:
    """Next/Back wizard shell (Story 6.1) - renders one step's frame at a time."""

    def __init__(self, steps: list[WizardStep]) -> None:
        self.steps = steps
        self.current_index = 0

        self.root = tk.Tk()
        self.root.title(_WINDOW_TITLE)

        self.content_frame = tk.Frame(self.root, padx=20, pady=20)
        self.content_frame.pack(fill="both", expand=True)

        nav = tk.Frame(self.root)
        nav.pack(fill="x", padx=20, pady=(0, 20))
        self.back_button = tk.Button(nav, text="Back", command=self.go_back)
        self.back_button.pack(side="left")
        self.next_button = tk.Button(nav, text="Next", command=self.go_next)
        self.next_button.pack(side="right")

        self._show_step(0)

    def _show_step(self, index: int) -> None:
        for child in self.content_frame.winfo_children():
            child.destroy()

        self.current_index = index
        step = self.steps[index]
        step.build(self.content_frame).pack(fill="both", expand=True)

        self.back_button.config(state="normal" if index > 0 else "disabled")
        self.next_button.config(text="Finish" if index == len(self.steps) - 1 else "Next")

        on_shown = getattr(step, "on_shown", None)
        if on_shown is not None:
            on_shown()

    def go_next(self) -> None:
        if self.current_index < len(self.steps) - 1:
            self._show_step(self.current_index + 1)
        else:
            on_finish = getattr(self.steps[self.current_index], "on_finish", None)
            if on_finish is not None:
                on_finish()
            self.root.destroy()

    def go_back(self) -> None:
        if self.current_index > 0:
            self._show_step(self.current_index - 1)

    def run(self) -> None:
        self.root.mainloop()
