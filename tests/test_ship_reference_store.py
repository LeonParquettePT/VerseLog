from verselog.core.ship_reference import ShipReference
from verselog.core.ship_reference_store import ShipReferenceStore

ARROW = ShipReference(
    name="MISC Starlancer MAX",
    cargo_capacity_scu=8,
    quantum_fuel_capacity=3.6,
    quantum_range=660550458716.0,
    fuel_usage_main=331.25,
    quantum_speed=171000000.0,
    quantum_spool_time=6.0,
)


def test_get_returns_none_for_unknown_ship(tmp_path):
    store = ShipReferenceStore(db_path=tmp_path / "verselog.db")

    assert store.get_ship("Nonexistent Ship") is None


def test_save_then_get_round_trips(tmp_path):
    store = ShipReferenceStore(db_path=tmp_path / "verselog.db")

    store.save_ships([ARROW])

    assert store.get_ship("MISC Starlancer MAX") == ARROW


def test_saving_the_same_ship_twice_updates_rather_than_duplicates(tmp_path):
    store = ShipReferenceStore(db_path=tmp_path / "verselog.db")
    store.save_ships([ARROW])

    updated = ShipReference(**{**vars(ARROW), "cargo_capacity_scu": 10})
    store.save_ships([updated])

    assert store.get_ship("MISC Starlancer MAX").cargo_capacity_scu == 10
