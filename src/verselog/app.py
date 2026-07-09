from verselog.adapters.capture.benchmark import Benchmark
from verselog.adapters.capture.ocr_provider import OCRProvider
from verselog.adapters.capture.vision_provider import VisionProvider
from verselog.adapters.trigger.manual_trigger import ManualTriggerAdapter
from verselog.adapters.ui.console_ui_provider import ConsoleUIProvider
from verselog.core.loading_plan_calculator import LoadingPlanCalculator
from verselog.core.location_reference_store import LocationReferenceStore
from verselog.core.ports.capture_port import CapturePort
from verselog.core.ports.ui_port import UIPort
from verselog.core.route_cost_calculator import RouteCostCalculator
from verselog.core.scan_result import ScanResult
from verselog.core.settings_store import SettingsStore
from verselog.core.ship_reference_store import ShipReferenceStore
from verselog.core.trust_layer import TrustLayer

_TIME_BUDGET_SECONDS = 30.0
_FALLBACK_TIER_NAME = "ocr"


def _select_capture_port(
    settings_store: SettingsStore, candidates: list[tuple[str, CapturePort]]
) -> CapturePort:
    benchmark = Benchmark()

    if benchmark.should_rerun(settings_store):
        result = benchmark.run(candidates, _TIME_BUDGET_SECONDS)
        benchmark.persist(result, settings_store)
        tier_name = result.tier_name
    else:
        tier_name = settings_store.get("benchmark_tier_name", _FALLBACK_TIER_NAME)

    for name, provider in candidates:
        if name == tier_name:
            return provider

    for name, provider in candidates:
        if name == _FALLBACK_TIER_NAME:
            return provider

    return candidates[-1][1]


def run(
    ship_name: str,
    *,
    capture_port: CapturePort | None = None,
    settings_store: SettingsStore | None = None,
    ship_store: ShipReferenceStore | None = None,
    location_store: LocationReferenceStore | None = None,
    trust_layer: TrustLayer | None = None,
    ui: UIPort | None = None,
) -> None:
    settings_store = settings_store if settings_store is not None else SettingsStore()
    ship_store = ship_store if ship_store is not None else ShipReferenceStore()
    location_store = location_store if location_store is not None else LocationReferenceStore()
    trust_layer = trust_layer if trust_layer is not None else TrustLayer()
    ui = ui if ui is not None else ConsoleUIProvider()

    route_cost_calculator = RouteCostCalculator(location_store, ship_store)
    loading_plan_calculator = LoadingPlanCalculator(route_cost_calculator)

    if capture_port is None:
        candidates: list[tuple[str, CapturePort]] = [("vision", VisionProvider()), ("ocr", OCRProvider())]
        capture_port = _select_capture_port(settings_store, candidates)

    trigger = ManualTriggerAdapter(capture_port)

    capture_result = trigger.on_triggered()
    trust_result = trust_layer.process(capture_result)

    if trust_result.contract is None:
        scan_result = ScanResult(
            contract=None,
            route_cost=None,
            loading_plan=None,
            quarantine_reasons=trust_result.reasons,
        )
    else:
        contract = trust_result.contract
        try:
            route_cost = route_cost_calculator.calculate(contract.departure, contract.arrival, ship_name)
            loading_plan = loading_plan_calculator.derive(contract, ship_name)
        except ValueError:
            route_cost = None
            loading_plan = None
        scan_result = ScanResult(contract=contract, route_cost=route_cost, loading_plan=loading_plan)

    ui.show_results([scan_result])
