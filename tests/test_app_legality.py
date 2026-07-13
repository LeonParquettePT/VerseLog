from verselog.app import run
from verselog.core.capture_result import CaptureResult
from verselog.core.contract import Contract
from verselog.core.legality_checker import LegalityRisk
from verselog.core.location_reference import LocationReference
from verselog.core.location_reference_store import LocationReferenceStore
from verselog.core.ports.capture_port import CapturePort
from verselog.core.scan_result import ScanResult
from verselog.core.settings_store import SettingsStore
from verselog.core.ship_reference import ShipReference
from verselog.core.ship_reference_store import ShipReferenceStore
from verselog.core.trust_layer import TrustLayer


class _FakeCapturePort(CapturePort):
    def __init__(self, result: CaptureResult) -> None:
        self._result = result

    def capture(self) -> CaptureResult:
        return self._result


class _FakeLegalityChecker:
    def __init__(self, risk: LegalityRisk | None) -> None:
        self._risk = risk
        self.checked_contracts = []

    def check(self, contract):
        self.checked_contracts.append(contract)
        return self._risk


class _SpyUI:
    def __init__(self, confirm_result: bool | Exception = True) -> None:
        self.shown: list[ScanResult] = []
        self._confirm_result = confirm_result
        self.confirm_calls = []

    def show_results(self, results: list[ScanResult]) -> None:
        self.shown.extend(results)

    def confirm_risky_contract(self, contract, risk) -> bool:
        self.confirm_calls.append((contract, risk))
        if isinstance(self._confirm_result, Exception):
            raise self._confirm_result
        return self._confirm_result

    def select_ship(self, ship_names):
        raise AssertionError("select_ship should never be called when ship_name is given explicitly")

    def warn_missing_prerequisites(self, missing) -> None:
        pass


class _StubPrerequisiteChecker:
    def check_missing(self):
        return []


def _stores(tmp_path):
    ship_store = ShipReferenceStore(db_path=tmp_path / "verselog.db")
    location_store = LocationReferenceStore(db_path=tmp_path / "verselog.db")
    ship_store.save_ships(
        [
            ShipReference(
                name="MISC Starlancer MAX",
                cargo_capacity_scu=8,
                quantum_fuel_capacity=3.6,
                quantum_range=660550458716.0,
                fuel_usage_main=331.25,
                quantum_speed=171000000.0,
                quantum_spool_time=6.0,
            )
        ]
    )
    location_store.save_locations(
        [
            LocationReference(
                name="Port Tressler", system="stanton",
                x=22462646723.530945, y=37186290817.84713, z=808831.762531,
            ),
            LocationReference(
                name="Greycat Stanton IV Production Complex-A", system="stanton",
                x=22461661905.144794, y=37185603796.0801, z=-895144.87,
            ),
        ]
    )
    return ship_store, location_store


def _run(tmp_path, contract, legality_checker, ui):
    ship_store, location_store = _stores(tmp_path)
    capture_port = _FakeCapturePort(CaptureResult(contract=contract, source_image=b"png"))

    run(
        ship_name="MISC Starlancer MAX",
        capture_port=capture_port,
        settings_store=SettingsStore(path=tmp_path / "settings.json"),
        ship_store=ship_store,
        location_store=location_store,
        trust_layer=TrustLayer(quarantine_dir=tmp_path / "quarantine"),
        ui=ui,
        legality_checker=legality_checker,
        prerequisite_checker=_StubPrerequisiteChecker(),
    )


def _contract():
    return Contract(
        departure="Port Tressler",
        arrival="Greycat Stanton IV Production Complex-A",
        scu=6,
        reward=50250.0,
    )


def test_declined_contract_is_withheld_from_route_and_loading_calculation(tmp_path):
    risk = LegalityRisk(faction="Nine Tails", standing=10.0, reason="Standing too low.")
    checker = _FakeLegalityChecker(risk)
    ui = _SpyUI(confirm_result=False)

    _run(tmp_path, _contract(), checker, ui)

    assert len(ui.shown) == 1
    result = ui.shown[0]
    assert result.contract == _contract()
    assert result.declined_reason == "Standing too low."
    assert result.route_cost is None
    assert result.loading_plan is None
    assert len(ui.confirm_calls) == 1


def test_accepted_contract_still_gets_route_and_loading_computed(tmp_path):
    risk = LegalityRisk(faction="Nine Tails", standing=10.0, reason="Standing too low.")
    checker = _FakeLegalityChecker(risk)
    ui = _SpyUI(confirm_result=True)

    _run(tmp_path, _contract(), checker, ui)

    result = ui.shown[0]
    assert result.declined_reason is None
    assert result.route_cost is not None
    assert result.loading_plan is not None


def test_a_non_risky_contract_never_triggers_the_confirmation_prompt(tmp_path):
    checker = _FakeLegalityChecker(None)  # never flags anything
    ui = _SpyUI()

    _run(tmp_path, _contract(), checker, ui)

    assert checker.checked_contracts == [_contract()]
    assert ui.confirm_calls == []
    result = ui.shown[0]
    assert result.route_cost is not None


def test_no_legality_checker_behaves_exactly_like_story_4_1(tmp_path):
    ui = _SpyUI()

    _run(tmp_path, _contract(), None, ui)

    assert ui.confirm_calls == []
    result = ui.shown[0]
    assert result.route_cost is not None
    assert result.loading_plan is not None


def test_a_broken_confirmation_dialog_is_treated_as_a_decline(tmp_path):
    risk = LegalityRisk(faction="Nine Tails", standing=10.0, reason="Standing too low.")
    checker = _FakeLegalityChecker(risk)
    ui = _SpyUI(confirm_result=EOFError("stdin closed"))

    _run(tmp_path, _contract(), checker, ui)

    result = ui.shown[0]
    assert result.declined_reason is not None
    assert result.route_cost is None
    assert result.loading_plan is None
