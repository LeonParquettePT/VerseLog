import requests

from verselog.core.location_reference import LocationReference
from verselog.core.location_reference_store import LocationReferenceStore
from verselog.core.ports.datasource_port import DataSourcePort

_URL = "https://cdn.jsdelivr.net/gh/StarCitizenWiki/scunpacked-data@master/starmap_positions.json"
_USER_AGENT = "VerseLog (github.com/LeonParquettePT/VerseLog) - free open-source Star Citizen logistics tool"


class LocationDataError(Exception):
    """Raised when the location coordinate import fails."""


def _location_from_json(item: dict) -> LocationReference:
    return LocationReference(
        name=item["name"],
        system=item["system"],
        x=item["x"],
        y=item["y"],
        z=item["z"],
    )


class LocationDataProvider(DataSourcePort):
    """Imports real location coordinates from scunpacked-data's starmap_positions.json (AD-4).

    Unlike CommunityAPIProvider's ship data, this is a single static file - no pagination.
    """

    def __init__(self, store: LocationReferenceStore, http_get=requests.get) -> None:
        self._store = store
        self._http_get = http_get

    def refresh(self) -> None:
        response = self._http_get(_URL, headers={"User-Agent": _USER_AGENT})
        if response.status_code != 200:
            raise LocationDataError(f"location data source returned status {response.status_code}")

        payload = response.json()
        locations = [_location_from_json(item) for item in payload.get("entities", [])]
        self._store.save_locations(locations)
