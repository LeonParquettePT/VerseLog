from abc import ABC, abstractmethod

from verselog.core.contract import Contract


class UIPort(ABC):
    """Implemented by adapters/ui/* (the results window). Concrete needs arrive in later stories."""

    @abstractmethod
    def show_results(self, contracts: list[Contract]) -> None: ...
