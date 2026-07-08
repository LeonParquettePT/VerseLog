import pytest

from verselog.adapters.datasource.location_data_provider import LocationDataError, LocationDataProvider
from verselog.core.location_reference_store import LocationReferenceStore

_SAMPLE_PAYLOAD = {
    "entities": [
        {"uuid": "1", "name": "Port Tressler", "system": "stanton", "x": 1.0, "y": 2.0, "z": 3.0},
        {"uuid": "2", "name": "Stanton", "system": "stanton", "x": 0.0, "y": 0.0, "z": 0.0},
    ],
    "connections": [],
}


class _FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self._payload


def test_imports_all_entities_from_the_single_file(tmp_path):
    store = LocationReferenceStore(db_path=tmp_path / "verselog.db")
    fake_http_get = lambda url, headers=None: _FakeResponse(_SAMPLE_PAYLOAD)
    provider = LocationDataProvider(store, http_get=fake_http_get)

    provider.refresh()

    location = store.get_location("Port Tressler")
    assert location is not None
    assert location.system == "stanton"
    assert location.x == 1.0
    assert location.y == 2.0
    assert location.z == 3.0
    assert store.get_location("Stanton") is not None


def test_raises_location_data_error_on_non_200_status(tmp_path):
    store = LocationReferenceStore(db_path=tmp_path / "verselog.db")
    fake_http_get = lambda url, headers=None: _FakeResponse({}, status_code=503)
    provider = LocationDataProvider(store, http_get=fake_http_get)

    with pytest.raises(LocationDataError):
        provider.refresh()
