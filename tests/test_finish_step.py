import tkinter as tk
from pathlib import Path

import pytest

from verselog_installer.steps.finish_step import FinishStep


@pytest.fixture(scope="module")
def root():
    r = tk.Tk()
    yield r
    r.destroy()


def _checkbuttons(frame: tk.Frame) -> list[tk.Checkbutton]:
    return [child for child in frame.winfo_children() if isinstance(child, tk.Checkbutton)]


def _make_step(root, **kwargs) -> tuple[FinishStep, list, tk.Frame]:
    created: list = []
    step = FinishStep(
        target_path=Path("C:/fake/verselog.exe"),
        desktop_dir=Path("C:/fake/Desktop"),
        start_menu_dir=Path("C:/fake/StartMenu"),
        shortcut_creator=lambda shortcut_path, target_path: created.append((shortcut_path, target_path)),
        **kwargs,
    )
    frame = step.build(root)
    return step, created, frame


def test_build_shows_the_completion_message_and_two_checked_checkboxes(root):
    step, _, frame = _make_step(root)

    boxes = _checkbuttons(frame)
    assert len(boxes) == 2
    assert step._desktop_var.get() is True
    assert step._start_menu_var.get() is True


def test_on_finish_creates_both_shortcuts_when_both_are_checked(root):
    step, created, _frame = _make_step(root)

    step.on_finish()

    assert created == [
        (Path("C:/fake/Desktop") / "VerseLog.lnk", Path("C:/fake/verselog.exe")),
        (Path("C:/fake/StartMenu") / "VerseLog.lnk", Path("C:/fake/verselog.exe")),
    ]


def test_unchecking_desktop_skips_only_that_shortcut(root):
    step, created, _frame = _make_step(root)
    step._desktop_var.set(False)

    step.on_finish()

    assert created == [(Path("C:/fake/StartMenu") / "VerseLog.lnk", Path("C:/fake/verselog.exe"))]


def test_unchecking_both_creates_no_shortcuts_at_all(root):
    step, created, _frame = _make_step(root)
    step._desktop_var.set(False)
    step._start_menu_var.set(False)

    step.on_finish()

    assert created == []


def test_build_preserves_the_players_choice_across_a_back_then_next_re_entry(root):
    step, created, _frame = _make_step(root)
    step._desktop_var.set(False)

    step.build(root)  # simulates Back-then-Next re-entry

    assert step._desktop_var.get() is False
    assert step._start_menu_var.get() is True
