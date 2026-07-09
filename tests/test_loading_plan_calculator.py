import pytest

from verselog.core.contract import Contract
from verselog.core.loading_plan_calculator import LoadingPlanCalculator, LoadingStep
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


def _calculator(tmp_path):
    location_store, ship_store = _stores(tmp_path)
    route_cost_calculator = RouteCostCalculator(location_store, ship_store)
    return LoadingPlanCalculator(route_cost_calculator), location_store, ship_store


def test_derives_a_two_step_plan_from_simple_fixtures(tmp_path):
    calculator, location_store, ship_store = _calculator(tmp_path)
    location_store.save_locations(
        [
            LocationReference(name="Origin", system="stanton", x=0.0, y=0.0, z=0.0),
            LocationReference(name="Destination", system="stanton", x=3.0, y=4.0, z=0.0),
        ]
    )
    ship_store.save_ships(
        [
            ShipReference(
                name="Test Ship",
                cargo_capacity_scu=10,
                quantum_fuel_capacity=10.0,
                quantum_range=1000.0,
                fuel_usage_main=1.0,
                quantum_speed=1.0,
                quantum_spool_time=2.0,
            )
        ]
    )
    contract = Contract(departure="Origin", arrival="Destination", scu=6, reward=1000.0)

    plan = calculator.derive(contract, "Test Ship")

    assert plan.steps == [
        LoadingStep(location="Origin", action="load", scu=6),
        LoadingStep(location="Destination", action="unload", scu=6),
    ]


def test_matches_the_real_captured_contract_and_ship(tmp_path):
    # Same real coordinates and ship stats confirmed in Story 2.2
    # (test_route_cost_calculator.py) - MISC Starlancer MAX has an 8 SCU
    # cargo hold, which the real captured contract's 6 SCU fits.
    calculator, location_store, ship_store = _calculator(tmp_path)
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

    plan = calculator.derive(contract, "MISC Starlancer MAX")

    assert plan.steps == [
        LoadingStep(location="Port Tressler", action="load", scu=6),
        LoadingStep(location="Greycat Stanton IV Production Complex-A", action="unload", scu=6),
    ]


def test_raises_when_contract_scu_exceeds_ship_cargo_capacity(tmp_path):
    calculator, location_store, ship_store = _calculator(tmp_path)
    location_store.save_locations(
        [
            LocationReference(name="A", system="stanton", x=0, y=0, z=0),
            LocationReference(name="B", system="stanton", x=1, y=1, z=1),
        ]
    )
    ship_store.save_ships(
        [
            ShipReference(
                name="Small Ship",
                cargo_capacity_scu=4,
                quantum_fuel_capacity=10.0,
                quantum_range=1000.0,
                fuel_usage_main=1.0,
                quantum_speed=1.0,
                quantum_spool_time=1.0,
            )
        ]
    )
    contract = Contract(departure="A", arrival="B", scu=6, reward=100.0)

    with pytest.raises(ValueError, match="cargo capacity"):
        calculator.derive(contract, "Small Ship")


def test_propagates_the_route_calculators_unknown_location_error(tmp_path):
    calculator, location_store, ship_store = _calculator(tmp_path)
    contract = Contract(departure="Nowhere", arrival="Nowhere", scu=1, reward=1.0)

    with pytest.raises(ValueError, match="departure"):
        calculator.derive(contract, "Nothing")


def test_propagates_the_route_calculators_unknown_ship_error(tmp_path):
    calculator, location_store, ship_store = _calculator(tmp_path)
    location_store.save_locations(
        [
            LocationReference(name="A", system="stanton", x=0, y=0, z=0),
            LocationReference(name="B", system="stanton", x=1, y=1, z=1),
        ]
    )
    contract = Contract(departure="A", arrival="B", scu=1, reward=1.0)

    with pytest.raises(ValueError, match="ship"):
        calculator.derive(contract, "Nothing")
