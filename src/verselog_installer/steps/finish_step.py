import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path

_FONT = ("Segoe UI", 14)
_COMPLETION_MESSAGE = "VerseLog is ready to use!"
_SHORTCUT_NAME = "VerseLog.lnk"


def _default_target_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "verselog.exe"
    return Path("verselog.exe")


def _default_desktop_dir() -> Path:
    return Path.home() / "Desktop"


def _default_start_menu_dir() -> Path:
    return Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"


def _create_shortcut(shortcut_path: Path, target_path: Path) -> None:
    """Create a real Windows .lnk file via PowerShell's WScript.Shell COM automation.

    No pywin32 dependency needed for this one-shot action.
    """
    shortcut_path.parent.mkdir(parents=True, exist_ok=True)
    ps_script = (
        "$WshShell = New-Object -ComObject WScript.Shell; "
        f'$Shortcut = $WshShell.CreateShortcut("{shortcut_path}"); '
        f'$Shortcut.TargetPath = "{target_path}"; '
        "$Shortcut.Save()"
    )
    subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script], check=True)


class FinishStep:
    """Completion screen with optional shortcut creation (Story 6.3)."""

    title = "Finish"

    def __init__(
        self,
        target_path: Path | None = None,
        desktop_dir: Path | None = None,
        start_menu_dir: Path | None = None,
        shortcut_creator=_create_shortcut,
    ) -> None:
        self._target_path = target_path if target_path is not None else _default_target_path()
        self._desktop_dir = desktop_dir if desktop_dir is not None else _default_desktop_dir()
        self._start_menu_dir = start_menu_dir if start_menu_dir is not None else _default_start_menu_dir()
        self._shortcut_creator = shortcut_creator
        self._desktop_var: tk.BooleanVar | None = None
        self._start_menu_var: tk.BooleanVar | None = None

    def build(self, parent: tk.Frame) -> tk.Frame:
        frame = tk.Frame(parent)
        tk.Label(frame, text=_COMPLETION_MESSAGE, font=_FONT).pack(pady=(20, 16))

        # Preserve the player's own choice across Back-then-Next re-entries
        # (Story 6.2's own code-review lesson, applied proactively here).
        if self._desktop_var is None:
            self._desktop_var = tk.BooleanVar(value=True)
        if self._start_menu_var is None:
            self._start_menu_var = tk.BooleanVar(value=True)

        tk.Checkbutton(frame, text="Create a desktop shortcut", variable=self._desktop_var, font=_FONT).pack(
            anchor="w", pady=4
        )
        tk.Checkbutton(frame, text="Create a Start Menu shortcut", variable=self._start_menu_var, font=_FONT).pack(
            anchor="w", pady=4
        )
        return frame

    def on_finish(self) -> None:
        if self._desktop_var is not None and self._desktop_var.get():
            self._shortcut_creator(self._desktop_dir / _SHORTCUT_NAME, self._target_path)
        if self._start_menu_var is not None and self._start_menu_var.get():
            self._shortcut_creator(self._start_menu_dir / _SHORTCUT_NAME, self._target_path)
