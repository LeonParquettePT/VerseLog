from verselog.core.location_reference import LocationReference
from verselog.core.location_reference_store import LocationReferenceStore

PORT_TRESSLER = LocationReference(
    name="Port Tressler", system="stanton", x=22462646723.53, y=37186290817.85, z=808831.76
)


def test_get_returns_none_for_unknown_location(tmp_path):
    store = LocationReferenceStore(db_path=tmp_path / "verselog.db")

    assert store.get_location("Nonexistent") is None


def test_save_then_get_round_trips(tmp_path):
    store = LocationReferenceStore(db_path=tmp_path / "verselog.db")

    store.save_locations([PORT_TRESSLER])

    assert store.get_location("Port Tressler") == PORT_TRESSLER


def test_saving_the_same_location_twice_updates_rather_than_duplicates(tmp_path):
    store = LocationReferenceStore(db_path=tmp_path / "verselog.db")
    store.save_locations([PORT_TRESSLER])

    updated = LocationReference(**{**vars(PORT_TRESSLER), "x": 0.0})
    store.save_locations([updated])

    assert store.get_location("Port Tressler").x == 0.0
