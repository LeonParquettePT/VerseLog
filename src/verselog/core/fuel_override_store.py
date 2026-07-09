from verselog.core.settings_store import SettingsStore

_SETTINGS_KEY = "fuel_overrides"


class FuelOverrideStore:
    """Per-ship fuel-per-meter overrides, layered on the single settings store (AD-7)."""

    def __init__(self, settings_store: SettingsStore) -> None:
        self._settings_store = settings_store

    def set_override(self, ship_name: str, fuel_per_meter: float) -> None:
        if fuel_per_meter <= 0:
            raise ValueError(f"fuel override must be positive, got {fuel_per_meter}")
        overrides = self._settings_store.get(_SETTINGS_KEY, {})
        overrides[ship_name] = fuel_per_meter
        self._settings_store.set(_SETTINGS_KEY, overrides)

    def get_override(self, ship_name: str) -> float | None:
        return self._settings_store.get(_SETTINGS_KEY, {}).get(ship_name)

    def reset(self, ship_name: str) -> None:
        overrides = self._settings_store.get(_SETTINGS_KEY, {})
        if ship_name in overrides:
            del overrides[ship_name]
            self._settings_store.set(_SETTINGS_KEY, overrides)
