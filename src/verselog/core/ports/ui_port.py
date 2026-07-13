from abc import ABC, abstractmethod

from verselog.core.contract import Contract
from verselog.core.legality_checker import LegalityRisk
from verselog.core.missing_prerequisite import MissingPrerequisite
from verselog.core.scan_result import ScanResult


class UIPort(ABC):
    """Implemented by adapters/ui/* (the results window). Concrete needs arrive in later stories."""

    @abstractmethod
    def show_results(self, results: list[ScanResult]) -> None: ...

    @abstractmethod
    def confirm_risky_contract(self, contract: Contract, risk: LegalityRisk) -> bool:
        """Ask the player whether to proceed on a flagged contract.

        Returns only the player's reported choice (True = proceed, False =
        decline) for the tool's own internal handling. Implementations must
        never perform the accept/decline as an in-game action themselves -
        no input injection (see SPEC.md non-goals).
        """
        ...

    @abstractmethod
    def warn_missing_prerequisites(self, missing: list[MissingPrerequisite]) -> None:
        """Tell the player which third-party prerequisites (Tesseract, Ollama) are missing.

        Purely informational - never installs anything, never blocks the
        scan. Implementations must do nothing when the list is empty.
        """
        ...

    @abstractmethod
    def select_ship(self, ship_names: list[str]) -> str | None:
        """Ask the player which ship to use, when none was given on the command line.

        Returns the chosen name, or None if the player cancelled/closed
        without picking (or there was nothing to pick from) - callers must
        treat None as "stop here", the same fail-closed spirit as
        confirm_risky_contract.
        """
        ...
