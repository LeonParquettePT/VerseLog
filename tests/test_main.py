import pytest

from verselog import __main__ as verselog_main
from verselog.adapters.ui.console_ui_provider import ConsoleUIProvider
from verselog.adapters.ui.tkinter_ui_provider import TkinterUIProvider


class _SpyRun:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def __call__(self, **kwargs) -> None:
        self.calls.append(kwargs)


def test_defaults_to_the_tkinter_ui(monkeypatch):
    spy = _SpyRun()
    monkeypatch.setattr(verselog_main, "run", spy)
    monkeypatch.setattr("sys.argv", ["verselog", "--ship", "MISC Starlancer MAX"])

    verselog_main.main()

    assert len(spy.calls) == 1
    assert isinstance(spy.calls[0]["ui"], TkinterUIProvider)
    assert spy.calls[0]["ship_name"] == "MISC Starlancer MAX"


def test_console_ui_flag_selects_the_console_provider(monkeypatch):
    spy = _SpyRun()
    monkeypatch.setattr(verselog_main, "run", spy)
    monkeypatch.setattr("sys.argv", ["verselog", "--ship", "MISC Starlancer MAX", "--console-ui"])

    verselog_main.main()

    assert isinstance(spy.calls[0]["ui"], ConsoleUIProvider)


def test_console_ui_without_ship_still_errors(monkeypatch, capsys):
    monkeypatch.setattr(verselog_main, "run", _SpyRun())
    monkeypatch.setattr("sys.argv", ["verselog", "--console-ui"])

    with pytest.raises(SystemExit):
        verselog_main.main()

    assert "--ship is required" in capsys.readouterr().err


def test_default_tkinter_ui_without_ship_lets_the_ui_pick_the_ship(monkeypatch):
    spy = _SpyRun()
    monkeypatch.setattr(verselog_main, "run", spy)
    monkeypatch.setattr("sys.argv", ["verselog"])

    verselog_main.main()

    assert len(spy.calls) == 1
    assert isinstance(spy.calls[0]["ui"], TkinterUIProvider)
    assert spy.calls[0]["ship_name"] is None
