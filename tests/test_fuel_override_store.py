import pytest

from verselog.core.fuel_override_store import FuelOverrideStore
from verselog.core.settings_store import SettingsStore


def _store(tmp_path):
    return FuelOverrideStore(SettingsStore(path=tmp_path / "settings.json"))


def test_get_override_returns_none_when_unset(tmp_path):
    store = _store(tmp_path)

    assert store.get_override("MISC Starlancer MAX") is None


def test_set_then_get_returns_the_exact_value(tmp_path):
    store = _store(tmp_path)

    store.set_override("MISC Starlancer MAX", 0.005)

    assert store.get_override("MISC Starlancer MAX") == 0.005


def test_set_override_rejects_non_positive_values(tmp_path):
    store = _store(tmp_path)

    with pytest.raises(ValueError):
        store.set_override("MISC Starlancer MAX", 0.0)

    with pytest.raises(ValueError):
        store.set_override("MISC Starlancer MAX", -1.0)


def test_reset_clears_a_previously_set_override(tmp_path):
    store = _store(tmp_path)
    store.set_override("MISC Starlancer MAX", 0.005)

    store.reset("MISC Starlancer MAX")

    assert store.get_override("MISC Starlancer MAX") is None


def test_reset_is_a_no_op_when_nothing_was_set(tmp_path):
    store = _store(tmp_path)

    store.reset("MISC Starlancer MAX")  # must not raise

    assert store.get_override("MISC Starlancer MAX") is None


def test_overrides_persist_across_store_instances(tmp_path):
    settings_path = tmp_path / "settings.json"
    FuelOverrideStore(SettingsStore(path=settings_path)).set_override("Nox", 0.01)

    reloaded = FuelOverrideStore(SettingsStore(path=settings_path))

    assert reloaded.get_override("Nox") == 0.01


def test_overrides_for_different_ships_are_independent(tmp_path):
    store = _store(tmp_path)
    store.set_override("MISC Starlancer MAX", 0.005)
    store.set_override("Nox", 0.01)

    store.reset("MISC Starlancer MAX")

    assert store.get_override("MISC Starlancer MAX") is None
    assert store.get_override("Nox") == 0.01
