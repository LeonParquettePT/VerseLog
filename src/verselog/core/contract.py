from dataclasses import dataclass


@dataclass
class Contract:
    """The one data shape allowed to cross a port boundary (see ARCHITECTURE-SPINE.md)."""

    departure: str
    arrival: str
    scu: int
    reward: float
    remaining_time: str | None = None
