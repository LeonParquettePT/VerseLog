import pytest

from verselog.adapters.datasource.community_api_provider import CommunityAPIError, CommunityAPIProvider
from verselog.core.ship_reference_store import ShipReferenceStore

# Shaped like the real, already-confirmed api.star-citizen.wiki /api/vehicles response.
_STARLANCER_JSON = {
    "name": "MISC Starlancer MAX",
    "cargo_capacity": 8,
    "quantum": {
        "quantum_speed": 171000000,
        "quantum_spool_time": 6,
        "quantum_fuel_capacity": 3.6,
        "quantum_range": 660550458716,
    },
    "fuel": {
        "capacity": 50,
        "usage": {"main": 331.25, "retro": 187.5, "vtol": 112.5, "maneuvering": 915},
    },
}

_ARROW_JSON = {
    "name": "MISC Freelancer",
    "cargo_capacity": 66,
    "quantum": {"quantum_fuel_capacity": 12.0, "quantum_range": 1_000_000.0},
    "fuel": {"usage": {"main": 50.0}},
}


class _FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self._payload


def test_imports_a_single_page_of_ships(tmp_path):
    store = ShipReferenceStore(db_path=tmp_path / "verselog.db")
    fake_http_get = lambda url, headers=None: _FakeResponse({"data": [_STARLANCER_JSON], "links": {}})
    provider = CommunityAPIProvider(store, http_get=fake_http_get)

    provider.refresh()

    ship = store.get_ship("MISC Starlancer MAX")
    assert ship is not None
    assert ship.cargo_capacity_scu == 8
    assert ship.quantum_fuel_capacity == 3.6
    assert ship.quantum_range == 660550458716
    assert ship.fuel_usage_main == 331.25
    assert ship.quantum_speed == 171000000
    assert ship.quantum_spool_time == 6


def test_follows_pagination_across_multiple_pages(tmp_path):
    store = ShipReferenceStore(db_path=tmp_path / "verselog.db")
    calls = []

    def fake_http_get(url, headers=None):
        calls.append(url)
        if url == "https://api.star-citizen.wiki/api/vehicles":
            return _FakeResponse({"data": [_STARLANCER_JSON], "links": {"next": "https://api.star-citizen.wiki/api/vehicles?page=2"}})
        return _FakeResponse({"data": [_ARROW_JSON], "links": {}})

    provider = CommunityAPIProvider(store, http_get=fake_http_get)
    provider.refresh()

    assert len(calls) == 2
    assert store.get_ship("MISC Starlancer MAX") is not None
    assert store.get_ship("MISC Freelancer") is not None


def test_raises_community_api_error_on_non_200_status(tmp_path):
    store = ShipReferenceStore(db_path=tmp_path / "verselog.db")
    fake_http_get = lambda url, headers=None: _FakeResponse({}, status_code=503)
    provider = CommunityAPIProvider(store, http_get=fake_http_get)

    with pytest.raises(CommunityAPIError):
        provider.refresh()
