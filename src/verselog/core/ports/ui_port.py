from abc import ABC, abstractmethod

from verselog.core.contract import Contract
from verselog.core.legality_checker import LegalityRisk


class UIPort(ABC):
    """Implemented by adapters/ui/* (the results window). Concrete needs arrive in later stories."""

    @abstractmethod
    def show_results(self, contracts: list[Contract]) -> None: ...

    @abstractmethod
    def confirm_risky_contract(self, contract: Contract, risk: LegalityRisk) -> bool:
        """Ask the player whether to proceed on a flagged contract.

        Returns only the player's reported choice (True = proceed, False =
        decline) for the tool's own internal handling. Implementations must
        never perform the accept/decline as an in-game action themselves -
        no input injection (see SPEC.md non-goals).
        """
        ...
