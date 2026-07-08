import time

import requests

from verselog.core.ports.datasource_port import DataSourcePort
from verselog.core.ship_reference import ShipReference
from verselog.core.ship_reference_store import ShipReferenceStore

_BASE_URL = "https://api.star-citizen.wiki/api/vehicles"
_USER_AGENT = "VerseLog (github.com/LeonParquettePT/VerseLog) - free open-source Star Citizen logistics tool"
_INTER_PAGE_DELAY_SECONDS = 0.2


class CommunityAPIError(Exception):
    """Raised when the bulk import from the community API fails."""


def _ship_from_json(item: dict) -> ShipReference:
    quantum = item.get("quantum") or {}
    fuel = item.get("fuel") or {}
    fuel_usage = fuel.get("usage") or {}
    return ShipReference(
        name=item["name"],
        cargo_capacity_scu=item.get("cargo_capacity") or 0,
        quantum_fuel_capacity=quantum.get("quantum_fuel_capacity") or 0.0,
        quantum_range=quantum.get("quantum_range") or 0.0,
        fuel_usage_main=fuel_usage.get("main") or 0.0,
        quantum_speed=quantum.get("quantum_speed") or 0.0,
        quantum_spool_time=quantum.get("quantum_spool_time") or 0.0,
    )


class CommunityAPIProvider(DataSourcePort):
    """Bulk-imports ship reference data from api.star-citizen.wiki into local SQLite (AD-4)."""

    def __init__(self, store: ShipReferenceStore, http_get=requests.get) -> None:
        self._store = store
        self._http_get = http_get

    def refresh(self) -> None:
        ships: list[ShipReference] = []
        url = _BASE_URL
        first_page = True

        while url:
            if not first_page:
                time.sleep(_INTER_PAGE_DELAY_SECONDS)
            first_page = False

            response = self._http_get(url, headers={"User-Agent": _USER_AGENT})
            if response.status_code != 200:
                raise CommunityAPIError(f"community API returned status {response.status_code} for {url}")

            payload = response.json()
            ships.extend(_ship_from_json(item) for item in payload.get("data", []))
            url = (payload.get("links") or {}).get("next")

        self._store.save_ships(ships)
