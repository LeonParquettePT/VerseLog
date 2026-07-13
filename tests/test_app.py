from verselog.app import _select_capture_port, run
from verselog.core.capture_result import CaptureResult
from verselog.core.contract import Contract
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
        self.capture_calls = 0

    def capture(self) -> CaptureResult:
        self.capture_calls += 1
        return self._result


class _SpyUI:
    def __init__(self, ship_to_select: str | None = None) -> None:
        self.shown: list[ScanResult] = []
        self._ship_to_select = ship_to_select
        self.select_ship_calls: list[list[str]] = []

    def show_results(self, results: list[ScanResult]) -> None:
        self.shown.extend(results)

    def confirm_risky_contract(self, contract, risk) -> bool:
        return True

    def select_ship(self, ship_names: list[str]) -> str | None:
        self.select_ship_calls.append(ship_names)
        return self._ship_to_select


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


def test_run_computes_route_and_loading_plan_for_a_valid_contract(tmp_path):
    ship_store, location_store = _stores(tmp_path)
    contract = Contract(
        departure="Port Tressler",
        arrival="Greycat Stanton IV Production Complex-A",
        scu=6,
        reward=50250.0,
    )
    capture_port = _FakeCapturePort(CaptureResult(contract=contract, source_image=b"png"))
    ui = _SpyUI()

    run(
        ship_name="MISC Starlancer MAX",
        capture_port=capture_port,
        settings_store=SettingsStore(path=tmp_path / "settings.json"),
        ship_store=ship_store,
        location_store=location_store,
        trust_layer=TrustLayer(quarantine_dir=tmp_path / "quarantine"),
        ui=ui,
    )

    assert len(ui.shown) == 1
    result = ui.shown[0]
    assert result.contract == contract
    assert result.route_cost is not None
    assert result.route_cost.distance_meters > 0
    assert result.loading_plan is not None
    assert result.loading_plan.steps[0].location == "Port Tressler"


def test_run_reports_quarantine_reasons_for_an_invalid_contract(tmp_path):
    ship_store, location_store = _stores(tmp_path)
    # scu <= 0 fails TrustLayer's validation (Story 1.3).
    contract = Contract(departure="Port Tressler", arrival="Greycat Stanton IV Production Complex-A", scu=0, reward=1.0)
    capture_port = _FakeCapturePort(CaptureResult(contract=contract, source_image=b"png"))
    ui = _SpyUI()

    run(
        ship_name="MISC Starlancer MAX",
        capture_port=capture_port,
        settings_store=SettingsStore(path=tmp_path / "settings.json"),
        ship_store=ship_store,
        location_store=location_store,
        trust_layer=TrustLayer(quarantine_dir=tmp_path / "quarantine"),
        ui=ui,
    )

    assert len(ui.shown) == 1
    result = ui.shown[0]
    assert result.contract is None
    assert any("scu" in reason for reason in result.quarantine_reasons)


def test_run_shows_the_contract_even_when_route_cost_calculation_fails(tmp_path):
    ship_store, location_store = _stores(tmp_path)
    # "Nowhere" isn't in the location store - RouteCostCalculator raises ValueError.
    contract = Contract(departure="Port Tressler", arrival="Nowhere", scu=6, reward=50250.0)
    capture_port = _FakeCapturePort(CaptureResult(contract=contract, source_image=b"png"))
    ui = _SpyUI()

    run(
        ship_name="MISC Starlancer MAX",
        capture_port=capture_port,
        settings_store=SettingsStore(path=tmp_path / "settings.json"),
        ship_store=ship_store,
        location_store=location_store,
        trust_layer=TrustLayer(quarantine_dir=tmp_path / "quarantine"),
        ui=ui,
    )

    result = ui.shown[0]
    assert result.contract == contract
    assert result.route_cost is None
    assert result.loading_plan is None


def test_run_keeps_the_computed_route_cost_even_when_loading_plan_derivation_fails(tmp_path):
    # A ship whose cargo capacity is smaller than the contract's SCU: the
    # route itself is perfectly valid (route_cost_calculator.calculate()
    # succeeds), but loading_plan_calculator.derive() raises on the capacity
    # check it does *in addition* to re-validating the same route. The
    # already-computed route_cost must survive that later, unrelated failure.
    ship_store, location_store = _stores(tmp_path)
    ship_store.save_ships(
        [
            ShipReference(
                name="Tiny Ship",
                cargo_capacity_scu=2,
                quantum_fuel_capacity=3.6,
                quantum_range=660550458716.0,
                fuel_usage_main=331.25,
                quantum_speed=171000000.0,
                quantum_spool_time=6.0,
            )
        ]
    )
    contract = Contract(
        departure="Port Tressler",
        arrival="Greycat Stanton IV Production Complex-A",
        scu=6,
        reward=50250.0,
    )
    capture_port = _FakeCapturePort(CaptureResult(contract=contract, source_image=b"png"))
    ui = _SpyUI()

    run(
        ship_name="Tiny Ship",
        capture_port=capture_port,
        settings_store=SettingsStore(path=tmp_path / "settings.json"),
        ship_store=ship_store,
        location_store=location_store,
        trust_layer=TrustLayer(quarantine_dir=tmp_path / "quarantine"),
        ui=ui,
    )

    result = ui.shown[0]
    assert result.contract == contract
    assert result.route_cost is not None
    assert result.route_cost.distance_meters > 0
    assert result.loading_plan is None


def test_select_capture_port_uses_the_persisted_tier_without_rerunning_the_benchmark(tmp_path):
    settings_store = SettingsStore(path=tmp_path / "settings.json")
    settings_store.set("benchmark_tier_name", "ocr")
    settings_store.set("benchmark_worker_count", 1)
    import os

    settings_store.set("benchmark_cpu_count", os.cpu_count())

    vision_calls = []
    ocr_calls = []

    class _CountingPort(CapturePort):
        def __init__(self, calls: list) -> None:
            self._calls = calls

        def capture(self) -> CaptureResult:
            self._calls.append(1)
            return CaptureResult(contract=None, source_image=b"", parse_error="not used")

    candidates = [("vision", _CountingPort(vision_calls)), ("ocr", _CountingPort(ocr_calls))]

    selected = _select_capture_port(settings_store, candidates)

    assert selected is candidates[1][1]
    # should_rerun was False (cpu count matches), so neither candidate's
    # capture() should have been invoked by the benchmark itself.
    assert vision_calls == []
    assert ocr_calls == []


def test_run_asks_the_ui_to_select_a_ship_when_none_is_given(tmp_path):
    ship_store, location_store = _stores(tmp_path)
    contract = Contract(
        departure="Port Tressler",
        arrival="Greycat Stanton IV Production Complex-A",
        scu=6,
        reward=50250.0,
    )
    capture_port = _FakeCapturePort(CaptureResult(contract=contract, source_image=b"png"))
    ui = _SpyUI(ship_to_select="MISC Starlancer MAX")

    run(
        ship_name=None,
        capture_port=capture_port,
        settings_store=SettingsStore(path=tmp_path / "settings.json"),
        ship_store=ship_store,
        location_store=location_store,
        trust_layer=TrustLayer(quarantine_dir=tmp_path / "quarantine"),
        ui=ui,
    )

    assert ui.select_ship_calls == [["MISC Starlancer MAX"]]
    result = ui.shown[0]
    assert result.route_cost is not None
    assert result.route_cost.ship.name == "MISC Starlancer MAX"


def test_run_stops_without_capturing_when_ship_selection_is_cancelled(tmp_path):
    ship_store, location_store = _stores(tmp_path)
    contract = Contract(
        departure="Port Tressler",
        arrival="Greycat Stanton IV Production Complex-A",
        scu=6,
        reward=50250.0,
    )
    capture_port = _FakeCapturePort(CaptureResult(contract=contract, source_image=b"png"))
    ui = _SpyUI(ship_to_select=None)

    run(
        ship_name=None,
        capture_port=capture_port,
        settings_store=SettingsStore(path=tmp_path / "settings.json"),
        ship_store=ship_store,
        location_store=location_store,
        trust_layer=TrustLayer(quarantine_dir=tmp_path / "quarantine"),
        ui=ui,
    )

    assert capture_port.capture_calls == 0
    assert ui.shown == []


def test_run_never_calls_select_ship_when_ship_name_is_given_explicitly(tmp_path):
    # Regression guard: VoiceAttack (Story 1.4) and any other caller that
    # already passes --ship must see zero behavior change from this story.
    ship_store, location_store = _stores(tmp_path)
    contract = Contract(
        departure="Port Tressler",
        arrival="Greycat Stanton IV Production Complex-A",
        scu=6,
        reward=50250.0,
    )
    capture_port = _FakeCapturePort(CaptureResult(contract=contract, source_image=b"png"))
    ui = _SpyUI(ship_to_select="should never be used")

    run(
        ship_name="MISC Starlancer MAX",
        capture_port=capture_port,
        settings_store=SettingsStore(path=tmp_path / "settings.json"),
        ship_store=ship_store,
        location_store=location_store,
        trust_layer=TrustLayer(quarantine_dir=tmp_path / "quarantine"),
        ui=ui,
    )

    assert ui.select_ship_calls == []
    assert capture_port.capture_calls == 1
