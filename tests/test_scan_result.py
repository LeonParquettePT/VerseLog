from verselog.core.contract import Contract
from verselog.core.loading_plan_calculator import LoadingPlan, LoadingStep
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


def test_describe_the_happy_path():
    contract = Contract(departure="Port Tressler", arrival="Greycat Stanton IV", scu=6, reward=50250.0)
    route_cost = RouteCost(distance_meters=2084562.91, travel_time_seconds=18.2, fuel_cost=11.4, ship=_ship())
    loading_plan = LoadingPlan(
        steps=[
            LoadingStep(location="Port Tressler", action="load", scu=6),
            LoadingStep(location="Greycat Stanton IV", action="unload", scu=6),
        ]
    )
    result = ScanResult(contract=contract, route_cost=route_cost, loading_plan=loading_plan)

    description = result.describe()

    assert "Port Tressler" in description
    assert "Greycat Stanton IV" in description
    assert "50250" in description or "50,250" in description
    assert "load" in description
    assert "unload" in description


def test_describe_the_quarantine_path():
    result = ScanResult(
        contract=None,
        route_cost=None,
        loading_plan=None,
        quarantine_reasons=["departure does not look like a station name: ''"],
    )

    description = result.describe()

    assert "does not look like a station name" in description
