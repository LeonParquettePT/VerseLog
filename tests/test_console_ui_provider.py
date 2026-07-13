from verselog.adapters.ui.console_ui_provider import ConsoleUIProvider
from verselog.core.contract import Contract
from verselog.core.legality_checker import LegalityRisk
from verselog.core.loading_plan_calculator import LoadingPlan, LoadingStep
from verselog.core.missing_prerequisite import MissingPrerequisite
from verselog.core.route_cost_calculator import RouteCost
from verselog.core.scan_result import ScanResult
from verselog.core.ship_reference import ShipReference


def _ship():
    return ShipReference(
        name="MISC Starlancer MAX",
        cargo_capacity_scu=8,
        quantum_fuel_capacity=3.6,
        quantum_range=660550458716.0,
        fuel_usage_main=331.25,
        quantum_speed=171000000.0,
        quantum_spool_time=6.0,
    )


def test_show_results_prints_the_happy_path(capsys):
    contract = Contract(departure="Port Tressler", arrival="Greycat Stanton IV", scu=6, reward=50250.0)
    route_cost = RouteCost(distance_meters=2084562.91, travel_time_seconds=18.2, fuel_cost=11.4, ship=_ship())
    loading_plan = LoadingPlan(
        steps=[
            LoadingStep(location="Port Tressler", action="load", scu=6),
            LoadingStep(location="Greycat Stanton IV", action="unload", scu=6),
        ]
    )
    result = ScanResult(contract=contract, route_cost=route_cost, loading_plan=loading_plan)

    ConsoleUIProvider().show_results([result])

    output = capsys.readouterr().out
    assert "Port Tressler" in output
    assert "Greycat Stanton IV" in output
    assert "50250" in output or "50,250" in output
    assert "load" in output
    assert "unload" in output


def test_show_results_prints_quarantine_reasons_when_no_contract(capsys):
    result = ScanResult(
        contract=None,
        route_cost=None,
        loading_plan=None,
        quarantine_reasons=["departure does not look like a station name: ''"],
    )

    ConsoleUIProvider().show_results([result])

    output = capsys.readouterr().out
    assert "does not look like a station name" in output


def test_confirm_risky_contract_returns_true_only_for_explicit_yes(monkeypatch, capsys):
    contract = Contract(departure="A", arrival="B", scu=1, reward=1.0)
    risk = LegalityRisk(faction="Nine Tails", standing=10.0, reason="Standing too low.")
    provider = ConsoleUIProvider()

    for answer, expected in [("y", True), ("Y", True), ("yes", True), ("YES", True), ("n", False), ("", False), ("nope", False)]:
        monkeypatch.setattr("builtins.input", lambda _prompt, answer=answer: answer)
        assert provider.confirm_risky_contract(contract, risk) is expected

    output = capsys.readouterr().out
    assert "Standing too low." in output


def test_select_ship_returns_the_chosen_name(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt: "2")

    result = ConsoleUIProvider().select_ship(["Aegis Avenger", "MISC Starlancer MAX"])

    assert result == "MISC Starlancer MAX"


def test_select_ship_returns_none_for_an_out_of_range_or_invalid_answer(monkeypatch):
    provider = ConsoleUIProvider()

    monkeypatch.setattr("builtins.input", lambda _prompt: "99")
    assert provider.select_ship(["Aegis Avenger"]) is None

    monkeypatch.setattr("builtins.input", lambda _prompt: "not a number")
    assert provider.select_ship(["Aegis Avenger"]) is None


def test_select_ship_returns_none_when_no_ships_are_available(capsys):
    result = ConsoleUIProvider().select_ship([])

    assert result is None
    assert "--import-reference-data" in capsys.readouterr().out


def test_warn_missing_prerequisites_prints_each_missing_item(capsys):
    missing = [
        MissingPrerequisite(name="Tesseract OCR", install_instructions="https://example.com/tesseract"),
        MissingPrerequisite(name="Ollama", install_instructions="https://example.com/ollama"),
    ]

    ConsoleUIProvider().warn_missing_prerequisites(missing)

    output = capsys.readouterr().out
    assert "Tesseract OCR" in output
    assert "https://example.com/tesseract" in output
    assert "Ollama" in output
    assert "https://example.com/ollama" in output


def test_warn_missing_prerequisites_prints_nothing_when_none_are_missing(capsys):
    ConsoleUIProvider().warn_missing_prerequisites([])

    assert capsys.readouterr().out == ""
