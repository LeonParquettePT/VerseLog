from abc import ABC, abstractmethod


class DataSourcePort(ABC):
    """Implemented by adapters/datasource/* (e.g. the community-API-backed local mirror). Concrete needs arrive in Epic 2 Story 2.1."""

    @abstractmethod
    def refresh(self) -> None: ...
