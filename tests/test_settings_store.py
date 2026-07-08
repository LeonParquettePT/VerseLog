from verselog.core.settings_store import SettingsStore


def test_get_returns_default_when_key_is_missing(tmp_path):
    store = SettingsStore(path=tmp_path / "settings.json")

    assert store.get("missing_key", "default_value") == "default_value"


def test_set_then_get_round_trips(tmp_path):
    store = SettingsStore(path=tmp_path / "settings.json")

    store.set("tier", "phi3-vision")

    assert store.get("tier") == "phi3-vision"


def test_persists_across_instances(tmp_path):
    path = tmp_path / "settings.json"
    SettingsStore(path=path).set("worker_count", 4)

    reloaded = SettingsStore(path=path)

    assert reloaded.get("worker_count") == 4
