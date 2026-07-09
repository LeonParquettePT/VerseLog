from dataclasses import dataclass

from verselog.core.contract import Contract
from verselog.core.reputation_store import ReputationStore


@dataclass
class LegalityRisk:
    faction: str
    standing: float
    reason: str


class LegalityChecker:
    """Flags a contract as potentially illegal based on synced reputation (CAP-5).

    `location_factions` is a plain injected mapping, not a persisted store -
    no verified location-to-faction data source exists yet (see Dev Notes in
    the story file). Missing data (an unmapped location, or a faction with no
    synced standing) is never treated as risky.
    """

    def __init__(
        self,
        reputation_store: ReputationStore,
        location_factions: dict[str, str],
        risk_threshold: float,
    ) -> None:
        self._reputation_store = reputation_store
        self._location_factions = location_factions
        self._risk_threshold = risk_threshold

    def check(self, contract: Contract) -> LegalityRisk | None:
        for location in (contract.departure, contract.arrival):
            faction = self._location_factions.get(location)
            if faction is None:
                continue

            standing = self._reputation_store.get_level(faction)
            if standing is None:
                continue

            if standing <= self._risk_threshold:
                return LegalityRisk(
                    faction=faction,
                    standing=standing,
                    reason=(
                        f"Your standing with {faction} is {standing:g}, at or below the risk "
                        f"threshold of {self._risk_threshold:g} - entering their territory at "
                        f"{location!r} may be flagged as trespassing."
                    ),
                )

        return None
