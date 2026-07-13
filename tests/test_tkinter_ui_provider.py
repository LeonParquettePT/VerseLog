import tkinter as tk
import tkinter.font

from verselog.adapters.ui.tkinter_ui_provider import TkinterUIProvider
from verselog.core.contract import Contract
from verselog.core.legality_checker import LegalityRisk
from verselog.core.scan_result import ScanResult


def _labels(root: tk.Tk) -> list[tk.Label]:
    return [child for child in root.winfo_children() for child in child.winfo_children() if isinstance(child, tk.Label)]


def test_build_results_window_renders_each_scan_result_as_a_label():
    contract = Contract(departure="Port Tressler", arrival="Greycat Stanton IV", scu=6, reward=50250.0)
    result = ScanResult(contract=contract, route_cost=None, loading_plan=None)

    root = TkinterUIProvider().build_results_window([result])
    try:
        labels = _labels(root)
        assert len(labels) == 1
        assert labels[0].cget("text") == result.describe()
    finally:
        root.destroy()


def test_build_results_window_uses_a_large_readable_font():
    result = ScanResult(contract=None, route_cost=None, loading_plan=None, quarantine_reasons=["x"])

    root = TkinterUIProvider().build_results_window([result])
    try:
        label = _labels(root)[0]
        font = tk.font.Font(font=label.cget("font"))
        assert font.actual("size") >= 14
    finally:
        root.destroy()


def test_build_results_window_renders_multiple_results():
    results = [
        ScanResult(contract=Contract(departure="A", arrival="B", scu=1, reward=1.0), route_cost=None, loading_plan=None),
        ScanResult(contract=Contract(departure="C", arrival="D", scu=2, reward=2.0), route_cost=None, loading_plan=None),
    ]

    root = TkinterUIProvider().build_results_window(results)
    try:
        labels = _labels(root)
        assert len(labels) == 2
    finally:
        root.destroy()


def test_confirm_risky_contract_passes_through_the_dialogs_answer(monkeypatch):
    contract = Contract(departure="A", arrival="B", scu=1, reward=1.0)
    risk = LegalityRisk(faction="Nine Tails", standing=10.0, reason="Standing too low.")
    seen = {}

    def fake_askyesno(title, message):
        seen["title"] = title
        seen["message"] = message
        return True

    monkeypatch.setattr("verselog.adapters.ui.tkinter_ui_provider.messagebox.askyesno", fake_askyesno)

    assert TkinterUIProvider().confirm_risky_contract(contract, risk) is True
    assert "Standing too low." in seen["message"]

    monkeypatch.setattr("verselog.adapters.ui.tkinter_ui_provider.messagebox.askyesno", lambda title, message: False)
    assert TkinterUIProvider().confirm_risky_contract(contract, risk) is False


def _comboboxes(root: tk.Tk):
    import tkinter.ttk as ttk

    return [child for child in root.winfo_children() if isinstance(child, ttk.Combobox)]


def test_build_ship_selection_window_prefills_a_combobox_with_the_ship_names():
    root = TkinterUIProvider().build_ship_selection_window(["Aegis Avenger", "MISC Starlancer MAX"])
    try:
        combos = _comboboxes(root)
        assert len(combos) == 1
        assert list(combos[0].cget("values")) == ["Aegis Avenger", "MISC Starlancer MAX"]
    finally:
        root.destroy()


def test_build_ship_selection_window_shows_a_message_when_no_ships_are_available():
    root = TkinterUIProvider().build_ship_selection_window([])
    try:
        assert _comboboxes(root) == []
        labels = [child for child in root.winfo_children() if isinstance(child, tk.Label)]
        assert any("--import-reference-data" in label.cget("text") for label in labels)
    finally:
        root.destroy()


def test_select_ship_returns_none_if_the_window_closes_without_a_selection():
    provider = TkinterUIProvider()
    root = provider.build_ship_selection_window(["Aegis Avenger"])
    root.destroy()

    assert provider._selected_ship is None
