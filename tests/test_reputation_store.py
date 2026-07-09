from verselog.core.reputation_store import ReputationLevel, ReputationStore
from verselog.core.settings_store import SettingsStore


def _store(tmp_path):
    return ReputationStore(SettingsStore(path=tmp_path / "settings.json"))


def test_get_level_returns_none_when_unset(tmp_path):
    store = _store(tmp_path)

    assert store.get_level("Covalex") is None


def test_set_then_get_returns_the_exact_value(tmp_path):
    store = _store(tmp_path)

    store.set_level("Covalex", 75.0)

    assert store.get_level("Covalex") == 75.0


def test_sync_updates_multiple_factions_independently(tmp_path):
    store = _store(tmp_path)

    store.sync(
        [
            ReputationLevel(faction="Covalex", standing=75.0),
            ReputationLevel(faction="Advocacy", standing=40.0),
        ]
    )

    assert store.get_level("Covalex") == 75.0
    assert store.get_level("Advocacy") == 40.0


def test_sync_with_an_empty_list_is_a_no_op(tmp_path):
    store = _store(tmp_path)
    store.set_level("Covalex", 75.0)

    store.sync([])

    assert store.get_level("Covalex") == 75.0


def test_set_level_after_sync_overrides_only_that_faction(tmp_path):
    store = _store(tmp_path)
    store.sync(
        [
            ReputationLevel(faction="Covalex", standing=75.0),
            ReputationLevel(faction="Advocacy", standing=40.0),
        ]
    )

    store.set_level("Covalex", 90.0)

    assert store.get_level("Covalex") == 90.0
    assert store.get_level("Advocacy") == 40.0


def test_levels_persist_across_store_instances(tmp_path):
    settings_path = tmp_path / "settings.json"
    ReputationStore(SettingsStore(path=settings_path)).set_level("Covalex", 75.0)

    reloaded = ReputationStore(SettingsStore(path=settings_path))

    assert reloaded.get_level("Covalex") == 75.0
