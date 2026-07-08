import math

import pytest

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


def test_calculates_distance_time_and_fuel_from_simple_fixtures(tmp_path):
    location_store, ship_store = _stores(tmp_path)
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
    calculator = RouteCostCalculator(location_store, ship_store)

    cost = calculator.calculate("Origin", "Destination", "Test Ship")

    assert cost.distance_meters == 5.0  # 3-4-5 triangle
    assert cost.travel_time_seconds == 2.0 + 5.0 / 1.0  # spool_time + distance/speed
    assert cost.fuel_cost == 5.0 * (10.0 / 1000.0)  # distance * (fuel_capacity/range)


def test_matches_the_real_captured_contract_locations(tmp_path):
    # Real coordinates from scunpacked-data's starmap_positions.json, verified
    # directly - the exact two locations from this project's own captured
    # contract example (contract-ui-reference.md).
    location_store, ship_store = _stores(tmp_path)
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
    calculator = RouteCostCalculator(location_store, ship_store)

    cost = calculator.calculate(
        "Port Tressler", "Greycat Stanton IV Production Complex-A", "MISC Starlancer MAX"
    )

    assert math.isclose(cost.distance_meters, 2084562.91, rel_tol=1e-6)
    assert cost.travel_time_seconds > 6.0  # at least the spool time
    assert cost.fuel_cost > 0


def test_raises_on_unknown_departure(tmp_path):
    location_store, ship_store = _stores(tmp_path)
    with pytest.raises(ValueError, match="departure"):
        RouteCostCalculator(location_store, ship_store).calculate("Nowhere", "Nowhere", "Nothing")


def test_raises_on_unknown_arrival(tmp_path):
    location_store, ship_store = _stores(tmp_path)
    location_store.save_locations([LocationReference(name="A", system="stanton", x=0, y=0, z=0)])

    with pytest.raises(ValueError, match="arrival"):
        RouteCostCalculator(location_store, ship_store).calculate("A", "Nowhere", "Nothing")


def test_raises_on_unknown_ship(tmp_path):
    location_store, ship_store = _stores(tmp_path)
    location_store.save_locations(
        [
            LocationReference(name="A", system="stanton", x=0, y=0, z=0),
            LocationReference(name="B", system="stanton", x=1, y=1, z=1),
        ]
    )

    with pytest.raises(ValueError, match="ship"):
        RouteCostCalculator(location_store, ship_store).calculate("A", "B", "Nothing")
