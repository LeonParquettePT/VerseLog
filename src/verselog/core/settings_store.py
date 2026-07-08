import json
from pathlib import Path
from typing import Any


class SettingsStore:
    """A single local JSON-backed key/value store, owned by the domain core (AD-7)."""

    def __init__(self, path: Path = Path("data/settings.json")) -> None:
        self._path = path
        if self._path.exists():
            self._data: dict[str, Any] = json.loads(self._path.read_text())
        else:
            self._data = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2))
