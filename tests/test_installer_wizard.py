import tkinter as tk

import pytest

from verselog_installer.wizard import InstallerWizard


class _FakeStep:
    def __init__(self, name: str) -> None:
        self.name = name
        self.title = name
        self.shown_count = 0

    def build(self, parent: tk.Frame) -> tk.Frame:
        frame = tk.Frame(parent)
        tk.Label(frame, text=self.name).pack()
        return frame

    def on_shown(self) -> None:
        self.shown_count += 1


def _labels_text(frame: tk.Frame) -> list[str]:
    return [
        grandchild.cget("text")
        for child in frame.winfo_children()
        for grandchild in child.winfo_children()
        if isinstance(grandchild, tk.Label)
    ]


def test_wizard_shows_the_first_step_on_construction():
    steps = [_FakeStep("Welcome"), _FakeStep("Benchmark")]
    wizard = InstallerWizard(steps)
    try:
        assert wizard.current_index == 0
        assert _labels_text(wizard.content_frame) == ["Welcome"]
        assert steps[0].shown_count == 1
    finally:
        wizard.root.destroy()


def test_go_next_advances_to_the_next_step_and_calls_on_shown():
    steps = [_FakeStep("Welcome"), _FakeStep("Benchmark")]
    wizard = InstallerWizard(steps)
    try:
        wizard.go_next()

        assert wizard.current_index == 1
        assert _labels_text(wizard.content_frame) == ["Benchmark"]
        assert steps[1].shown_count == 1
    finally:
        wizard.root.destroy()


def test_go_back_returns_to_the_previous_step():
    steps = [_FakeStep("Welcome"), _FakeStep("Benchmark")]
    wizard = InstallerWizard(steps)
    try:
        wizard.go_next()
        wizard.go_back()

        assert wizard.current_index == 0
        assert _labels_text(wizard.content_frame) == ["Welcome"]
    finally:
        wizard.root.destroy()


def test_back_button_is_disabled_on_the_first_step_only():
    steps = [_FakeStep("Welcome"), _FakeStep("Benchmark")]
    wizard = InstallerWizard(steps)
    try:
        assert str(wizard.back_button.cget("state")) == "disabled"

        wizard.go_next()
        assert str(wizard.back_button.cget("state")) == "normal"
    finally:
        wizard.root.destroy()


def test_next_button_says_finish_on_the_last_step():
    steps = [_FakeStep("Welcome"), _FakeStep("Benchmark")]
    wizard = InstallerWizard(steps)
    try:
        assert wizard.next_button.cget("text") == "Next"

        wizard.go_next()
        assert wizard.next_button.cget("text") == "Finish"
    finally:
        wizard.root.destroy()


def test_go_next_on_the_last_step_closes_the_wizard():
    steps = [_FakeStep("Welcome"), _FakeStep("Benchmark")]
    wizard = InstallerWizard(steps)
    wizard.go_next()

    wizard.go_next()

    # Once root.destroy() has torn down the whole interpreter, any further
    # Tcl call against it raises - that's the observable proof it's gone.
    with pytest.raises(tk.TclError):
        wizard.root.winfo_exists()
