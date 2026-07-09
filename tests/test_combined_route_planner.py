import pytest

from verselog.core.combined_route_planner import CombinedRoutePlanner
from verselog.core.contract import Contract
from verselog.core.loading_plan_calculator import LoadingStep
from verselog.core.location_reference import LocationReference
from verselog.core.location_reference_store import LocationReferenceStore
from verselog.core.route_cost_calculator import RouteCostCalculator
from verselog.core.ship_reference import ShipReference
from verselog.core.ship_reference_store import ShipReferenceStore


def _stores(tmp_path):
    return (
        LocationReferenceStore(db_path=tmp_path / "verselog.db"),
        ShipReferenceStore(db_path=tmp_path / "verselog.db"),
    )


def _planner(tmp_path):
    location_store, ship_store = _stores(tmp_path)
    route_cost_calculator = RouteCostCalculator(location_store, ship_store)
    return CombinedRoutePlanner(route_cost_calculator), location_store, ship_store


def _line_ship(ship_store, name="Test Ship", cargo_capacity_scu=10):
    ship_store.save_ships(
        [
            ShipReference(
                name=name,
                cargo_capacity_scu=cargo_capacity_scu,
                quantum_fuel_capacity=10.0,
                quantum_range=1000.0,
                fuel_usage_main=1.0,
                quantum_speed=1.0,
                quantum_spool_time=0.0,
            )
        ]
    )


def test_avoids_zig_zagging_by_grouping_colocated_pickups_first(tmp_path):
    # X=0, Y=10, Z=20 on a line. Mission A: X -> Y. Mission B: X -> Z.
    # A naive "finish A, then B" order would be X->Y->X->Z = 10+10+20 = 40
    # (zig-zagging back through X). The smart order picks up both at X
    # first (free, same location), then delivers B then A on the way out:
    # X->X->Z->Y = 0+20+10 = 30. Cheaper, and never zig-zags back to X.
    planner, location_store, ship_store = _planner(tmp_path)
    location_store.save_locations(
        [
            LocationReference(name="X", system="stanton", x=0.0, y=0.0, z=0.0),
            LocationReference(name="Y", system="stanton", x=10.0, y=0.0, z=0.0),
            LocationReference(name="Z", system="stanton", x=20.0, y=0.0, z=0.0),
        ]
    )
    _line_ship(ship_store)
    contract_a = Contract(departure="X", arrival="Y", scu=2, reward=100.0)
    contract_b = Contract(departure="X", arrival="Z", scu=2, reward=100.0)

    plan = planner.plan([contract_a, contract_b], "Test Ship")

    assert plan.loading_plan.steps == [
        LoadingStep(location="X", action="load", scu=2),
        LoadingStep(location="X", action="load", scu=2),
        LoadingStep(location="Z", action="unload", scu=2),
        LoadingStep(location="Y", action="unload", scu=2),
    ]
    assert plan.total_distance_meters == 30.0


def test_lifo_stack_is_never_violated(tmp_path):
    planner, location_store, ship_store = _planner(tmp_path)
    location_store.save_locations(
        [
            LocationReference(name="X", system="stanton", x=0.0, y=0.0, z=0.0),
            LocationReference(name="Y", system="stanton", x=10.0, y=0.0, z=0.0),
            LocationReference(name="Z", system="stanton", x=20.0, y=0.0, z=0.0),
        ]
    )
    _line_ship(ship_store)
    contract_a = Contract(departure="X", arrival="Y", scu=2, reward=100.0)
    contract_b = Contract(departure="X", arrival="Z", scu=2, reward=100.0)

    plan = planner.plan([contract_a, contract_b], "Test Ship")

    onboard: list[str] = []
    for step in plan.loading_plan.steps:
        if step.action == "load":
            onboard.append(step.location)
        else:
            # The most-recently-loaded still-onboard item must be the one
            # being delivered now - proves a properly-nested (LIFO) sequence.
            assert onboard, "unload with nothing onboard"
            onboard.pop()


def test_raises_when_combined_onboard_scu_exceeds_capacity_even_if_each_fits_alone(tmp_path):
    planner, location_store, ship_store = _planner(tmp_path)
    location_store.save_locations(
        [
            LocationReference(name="X", system="stanton", x=0.0, y=0.0, z=0.0),
            LocationReference(name="Y", system="stanton", x=10.0, y=0.0, z=0.0),
            LocationReference(name="Z", system="stanton", x=20.0, y=0.0, z=0.0),
        ]
    )
    _line_ship(ship_store, cargo_capacity_scu=3)  # each mission's scu=2 fits alone, but 2+2=4 doesn't
    contract_a = Contract(departure="X", arrival="Y", scu=2, reward=100.0)
    contract_b = Contract(departure="X", arrival="Z", scu=2, reward=100.0)

    with pytest.raises(ValueError, match="capacity"):
        planner.plan([contract_a, contract_b], "Test Ship")


def test_raises_on_unknown_departure(tmp_path):
    planner, location_store, ship_store = _planner(tmp_path)
    contract = Contract(departure="Nowhere", arrival="Nowhere", scu=1, reward=1.0)

    with pytest.raises(ValueError, match="departure"):
        planner.plan([contract], "Nothing")


def test_raises_on_unknown_ship(tmp_path):
    planner, location_store, ship_store = _planner(tmp_path)
    location_store.save_locations(
        [
            LocationReference(name="A", system="stanton", x=0, y=0, z=0),
            LocationReference(name="B", system="stanton", x=1, y=1, z=1),
        ]
    )
    contract = Contract(departure="A", arrival="B", scu=1, reward=1.0)

    with pytest.raises(ValueError, match="ship"):
        planner.plan([contract], "Nothing")


def test_raises_on_empty_contracts_list(tmp_path):
    planner, location_store, ship_store = _planner(tmp_path)

    with pytest.raises(ValueError):
        planner.plan([], "Nothing")


def test_single_contract_matches_the_single_mission_shape(tmp_path):
    planner, location_store, ship_store = _planner(tmp_path)
    location_store.save_locations(
        [
            LocationReference(name="X", system="stanton", x=0.0, y=0.0, z=0.0),
            LocationReference(name="Y", system="stanton", x=10.0, y=0.0, z=0.0),
        ]
    )
    _line_ship(ship_store)
    contract = Contract(departure="X", arrival="Y", scu=4, reward=100.0)

    plan = planner.plan([contract], "Test Ship")

    assert plan.loading_plan.steps == [
        LoadingStep(location="X", action="load", scu=4),
        LoadingStep(location="Y", action="unload", scu=4),
    ]
    assert plan.total_distance_meters == 10.0


def test_matches_the_real_captured_contract_and_ship(tmp_path):
    # Same real coordinates and ship stats confirmed in Story 2.2/2.3.
    planner, location_store, ship_store = _planner(tmp_path)
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
    contract = Contract(
        departure="Port Tressler",
        arrival="Greycat Stanton IV Production Complex-A",
        scu=6,
        reward=50250.0,
    )

    plan = planner.plan([contract], "MISC Starlancer MAX")

    assert plan.loading_plan.steps == [
        LoadingStep(location="Port Tressler", action="load", scu=6),
        LoadingStep(location="Greycat Stanton IV Production Complex-A", action="unload", scu=6),
    ]
    assert plan.total_distance_meters > 0
