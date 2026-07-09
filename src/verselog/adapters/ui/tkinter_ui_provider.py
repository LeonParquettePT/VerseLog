import tkinter as tk
from tkinter import messagebox

from verselog.core.contract import Contract
from verselog.core.legality_checker import LegalityRisk
from verselog.core.ports.ui_port import UIPort
from verselog.core.scan_result import ScanResult

_WINDOW_TITLE = "VerseLog — Results"
_FONT = ("Segoe UI", 14)


class TkinterUIProvider(UIPort):
    """The real results window (NFR9): simple, separate from the game, large readable text."""

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
