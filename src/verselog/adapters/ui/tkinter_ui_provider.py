import tkinter as tk
from tkinter import messagebox, ttk

from verselog.core.contract import Contract
from verselog.core.legality_checker import LegalityRisk
from verselog.core.missing_prerequisite import MissingPrerequisite
from verselog.core.ports.ui_port import UIPort
from verselog.core.scan_result import ScanResult

_WINDOW_TITLE = "VerseLog — Results"
_SHIP_SELECTION_TITLE = "VerseLog — Select Your Ship"
_FONT = ("Segoe UI", 14)
_NO_SHIPS_MESSAGE = "No ships found - run VerseLog with --import-reference-data first."


class TkinterUIProvider(UIPort):
    """The real results window (NFR9): simple, separate from the game, large readable text."""

    def __init__(self) -> None:
        self._selected_ship: str | None = None

    def show_results(self, results: list[ScanResult]) -> None:
        root = self.build_results_window(results)
        root.mainloop()

    def build_results_window(self, results: list[ScanResult]) -> tk.Tk:
        root = tk.Tk()
        root.title(_WINDOW_TITLE)

        for result in results:
            frame = tk.Frame(root, padx=12, pady=8)
            frame.pack(fill="x")
            tk.Label(frame, text=result.describe(), font=_FONT, justify="left", anchor="w").pack(fill="x")

        return root

    def confirm_risky_contract(self, contract: Contract, risk: LegalityRisk) -> bool:
        message = (
            f"{contract.departure} -> {contract.arrival}\n\n{risk.reason}\n\nProceed anyway?"
        )
        return messagebox.askyesno(title="VerseLog — Risky Contract", message=message)

    def select_ship(self, ship_names: list[str]) -> str | None:
        self._selected_ship = None
        root = self.build_ship_selection_window(ship_names)
        root.mainloop()
        return self._selected_ship

    def build_ship_selection_window(self, ship_names: list[str]) -> tk.Tk:
        root = tk.Tk()
        root.title(_SHIP_SELECTION_TITLE)

        if not ship_names:
            tk.Label(root, text=_NO_SHIPS_MESSAGE, font=_FONT, padx=12, pady=12).pack()
            tk.Button(root, text="Close", command=root.destroy).pack(pady=(0, 12))
            return root

        combo = ttk.Combobox(root, values=ship_names, state="readonly", font=_FONT)
        combo.current(0)
        combo.pack(padx=12, pady=12)

        def _confirm() -> None:
            self._selected_ship = combo.get()
            root.destroy()

        tk.Button(root, text="Start scan", command=_confirm).pack(pady=(0, 12))
        return root

    def warn_missing_prerequisites(self, missing: list[MissingPrerequisite]) -> None:
        if not missing:
            return
        lines = [f"{item.name}: {item.install_instructions}" for item in missing]
        message = "The following prerequisites are missing:\n\n" + "\n".join(lines)
        messagebox.showwarning(title="VerseLog — Missing Prerequisites", message=message)
