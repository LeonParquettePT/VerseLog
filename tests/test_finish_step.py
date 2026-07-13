import tkinter as tk
from pathlib import Path

import pytest

from verselog_installer.steps.finish_step import FinishStep, _ps_quote


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


def test_on_finish_shows_an_error_and_still_attempts_the_other_shortcut_when_one_fails(root):
    attempted: list = []

    def flaky_creator(shortcut_path: Path, target_path: Path) -> None:
        attempted.append(shortcut_path)
        if shortcut_path.parent == Path("C:/fake/Desktop"):
            raise RuntimeError("PowerShell execution is disabled by policy")

    shown: list = []
    step = FinishStep(
        target_path=Path("C:/fake/verselog.exe"),
        desktop_dir=Path("C:/fake/Desktop"),
        start_menu_dir=Path("C:/fake/StartMenu"),
        shortcut_creator=flaky_creator,
        message_shower=lambda title, message: shown.append((title, message)),
    )
    step.build(root)

    step.on_finish()  # must not raise, even though the desktop shortcut fails

    assert attempted == [
        Path("C:/fake/Desktop") / "VerseLog.lnk",
        Path("C:/fake/StartMenu") / "VerseLog.lnk",
    ]
    assert len(shown) == 1
    assert "PowerShell execution is disabled by policy" in shown[0][1]


def test_ps_quote_escapes_embedded_single_quotes_and_neutralizes_variable_expansion():
    path = Path("C:/Users/o'brien/$(calc)/verselog.exe")

    quoted = _ps_quote(path)

    assert quoted == "'" + str(path).replace("'", "''") + "'"
    # Single-quoted PowerShell strings never expand $variables or `$(...)`
    # subexpressions - the payload stays inert text, not executable code.
