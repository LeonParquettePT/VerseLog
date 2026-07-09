from verselog.core.contract import Contract
from verselog.core.legality_checker import LegalityChecker
from verselog.core.reputation_store import ReputationStore
from verselog.core.settings_store import SettingsStore


def _checker(tmp_path, location_factions, risk_threshold=25.0):
    reputation_store = ReputationStore(SettingsStore(path=tmp_path / "settings.json"))
    return LegalityChecker(reputation_store, location_factions, risk_threshold), reputation_store


def test_flags_a_contract_whose_departure_faction_standing_is_at_or_below_threshold(tmp_path):
    checker, reputation_store = _checker(tmp_path, {"Port Tressler": "Nine Tails"})
    reputation_store.set_level("Nine Tails", 10.0)
    contract = Contract(departure="Port Tressler", arrival="Somewhere Safe", scu=6, reward=100.0)

    risk = checker.check(contract)

    assert risk is not None
    assert risk.faction == "Nine Tails"
    assert risk.standing == 10.0
    assert "Nine Tails" in risk.reason
    assert "Port Tressler" in risk.reason


def test_does_not_flag_a_contract_whose_faction_standing_is_above_threshold(tmp_path):
    checker, reputation_store = _checker(tmp_path, {"Port Tressler": "Covalex"})
    reputation_store.set_level("Covalex", 80.0)
    contract = Contract(departure="Port Tressler", arrival="Somewhere Safe", scu=6, reward=100.0)

    assert checker.check(contract) is None


def test_does_not_flag_a_location_absent_from_the_faction_mapping(tmp_path):
    checker, reputation_store = _checker(tmp_path, {})
    contract = Contract(departure="Unmapped Place", arrival="Also Unmapped", scu=6, reward=100.0)

    assert checker.check(contract) is None


def test_does_not_flag_a_faction_with_no_synced_reputation_yet(tmp_path):
    checker, reputation_store = _checker(tmp_path, {"Port Tressler": "Nine Tails"})
    # Deliberately never call reputation_store.set_level - no synced data at all.
    contract = Contract(departure="Port Tressler", arrival="Somewhere Safe", scu=6, reward=100.0)

    assert checker.check(contract) is None


def test_checks_arrival_when_departure_is_safe(tmp_path):
    checker, reputation_store = _checker(
        tmp_path, {"Safe Departure": "Covalex", "Risky Arrival": "Nine Tails"}
    )
    reputation_store.set_level("Covalex", 80.0)
    reputation_store.set_level("Nine Tails", 5.0)
    contract = Contract(departure="Safe Departure", arrival="Risky Arrival", scu=6, reward=100.0)

    risk = checker.check(contract)

    assert risk is not None
    assert risk.faction == "Nine Tails"


def test_exact_threshold_boundary_is_flagged(tmp_path):
    checker, reputation_store = _checker(tmp_path, {"Port Tressler": "Nine Tails"}, risk_threshold=25.0)
    reputation_store.set_level("Nine Tails", 25.0)
    contract = Contract(departure="Port Tressler", arrival="Somewhere Safe", scu=6, reward=100.0)

    risk = checker.check(contract)

    assert risk is not None
    assert risk.standing == 25.0
