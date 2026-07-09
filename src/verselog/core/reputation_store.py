from dataclasses import dataclass

from verselog.core.settings_store import SettingsStore

_SETTINGS_KEY = "reputation_levels"


@dataclass
class ReputationLevel:
    faction: str
    standing: float


class ReputationStore:
    """Per-faction reputation standing, layered on the single settings store (AD-7)."""

    def __init__(self, settings_store: SettingsStore) -> None:
        self._settings_store = settings_store

    def set_level(self, faction: str, standing: float) -> None:
        levels = self._settings_store.get(_SETTINGS_KEY, {})
        levels[faction] = standing
        self._settings_store.set(_SETTINGS_KEY, levels)

    def get_level(self, faction: str) -> float | None:
        return self._settings_store.get(_SETTINGS_KEY, {}).get(faction)

    def sync(self, detected_levels: list[ReputationLevel]) -> None:
        if not detected_levels:
            return
        levels = self._settings_store.get(_SETTINGS_KEY, {})
        for level in detected_levels:
            levels[level.faction] = level.standing
        self._settings_store.set(_SETTINGS_KEY, levels)
