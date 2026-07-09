import math

import pytest

from verselog.core.fuel_override_store import FuelOverrideStore
from verselog.core.location_reference import LocationReference
from verselog.core.location_reference_store import LocationReferenceStore
from verselog.core.route_cost_calculator import RouteCostCalculator
from verselog.core.settings_store import SettingsStore
from verselog.core.ship_reference import ShipReference
from verselog.core.ship_reference_store import ShipReferenceStore


def _stores(tmp_path):
    return (
        LocationReferenceStore(db_path=tmp_path / "verselog.db"),
        ShipReferenceStore(db_path=tmp_path / "verselog.db"),
    )


def _simple_fixture(tmp_path, fuel_override_store=None):
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
    return RouteCostCalculator(location_store, ship_store, fuel_override_store)


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
    assert cost.ship.name == "Test Ship"  # already-fetched ship, no second lookup needed by callers


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


def test_raises_a_clear_error_for_a_ship_with_no_quantum_drive(tmp_path):
    # Real data confirms this: ground vehicles (e.g. the Nox speeder bike)
    # have quantum_speed/quantum_range = None from the API, defaulted to 0.0
    # by _ship_from_json. Must not crash with a raw ZeroDivisionError.
    location_store, ship_store = _stores(tmp_path)
    location_store.save_locations(
        [
            LocationReference(name="A", system="stanton", x=0, y=0, z=0),
            LocationReference(name="B", system="stanton", x=1, y=1, z=1),
        ]
    )
    ship_store.save_ships(
        [
            ShipReference(
                name="Nox",
                cargo_capacity_scu=0,
                quantum_fuel_capacity=0.0,
                quantum_range=0.0,
                fuel_usage_main=0.0,
                quantum_speed=0.0,
                quantum_spool_time=0.0,
            )
        ]
    )

    with pytest.raises(ValueError, match="quantum drive"):
        RouteCostCalculator(location_store, ship_store).calculate("A", "B", "Nox")


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


def test_uses_the_fuel_override_rate_instead_of_the_default_when_one_is_set(tmp_path):
    fuel_override_store = FuelOverrideStore(SettingsStore(path=tmp_path / "settings.json"))
    fuel_override_store.set_override("Test Ship", 2.0)
    calculator = _simple_fixture(tmp_path, fuel_override_store)

    cost = calculator.calculate("Origin", "Destination", "Test Ship")

    assert cost.fuel_cost == 5.0 * 2.0  # distance * override rate, not the default ratio


def test_falls_back_to_the_default_fuel_formula_when_no_override_is_set_for_that_ship(tmp_path):
    fuel_override_store = FuelOverrideStore(SettingsStore(path=tmp_path / "settings.json"))
    calculator = _simple_fixture(tmp_path, fuel_override_store)

    cost = calculator.calculate("Origin", "Destination", "Test Ship")

    assert cost.fuel_cost == 5.0 * (10.0 / 1000.0)  # unchanged default formula


def test_falls_back_to_the_default_fuel_formula_after_reset(tmp_path):
    fuel_override_store = FuelOverrideStore(SettingsStore(path=tmp_path / "settings.json"))
    fuel_override_store.set_override("Test Ship", 2.0)
    calculator = _simple_fixture(tmp_path, fuel_override_store)

    fuel_override_store.reset("Test Ship")
    cost = calculator.calculate("Origin", "Destination", "Test Ship")

    assert cost.fuel_cost == 5.0 * (10.0 / 1000.0)


def test_no_fuel_override_store_at_all_behaves_like_before_this_story(tmp_path):
    # The 2-argument construction Stories 2.2/2.3/2.4 already use, unmodified.
    calculator = _simple_fixture(tmp_path, fuel_override_store=None)

    cost = calculator.calculate("Origin", "Destination", "Test Ship")

    assert cost.fuel_cost == 5.0 * (10.0 / 1000.0)
