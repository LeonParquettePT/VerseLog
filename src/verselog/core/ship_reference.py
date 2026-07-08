from dataclasses import dataclass


@dataclass
class ShipReference:
    """A ship's cargo/fuel/quantum stats, imported in bulk from CommunityAPIProvider."""

    name: str
    cargo_capacity_scu: int
    quantum_fuel_capacity: float
    quantum_range: float
    fuel_usage_main: float
